from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, DialogAccessFilter, ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance
from django.conf import settings
from django.utils.translation import gettext as _

from bot.dialogs.dialog_buttons import punishment
from bot.dialogs.dialog_menus import punishments, hidden_mines_field
from bot.dialogs.dialog_texts import game_creation_texts, hidden_mines_game_texts
from bot.middlewares import set_random_choice_game_middlewares
from bot.models import AccessSettingsObject, User, ChatMember
from games.models import HiddenMinesGame, HiddenMinesGamePlayer
from shared import category

game_creation_router = Router()
game_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
game_creation_router.callback_query.filter(DialogAccessFilter(), DialogFilter("hidden_mines_game_creation"))
set_random_choice_game_middlewares(game_creation_router)


@game_creation_router.message(Command(settings.HIDDEN_MINES_GAME_COMMAND))
async def create_hidden_mines_game(message: Message, access_settings: AccessSettingsObject, user: User, member: ChatMember,
                                   dialog_manager: DialogManager, state: FSMContext, bot):
    await state.clear()

    if not access_settings.can_create_games:
        await message.answer(_("You cannot create games"))
        await message.delete()
        return

    dialog = Dialog.create("hidden_mines_game_creation", user_id=member.user_id, chat_id=member.chat_id, bot=bot)
    dialog.data["prefix"] = _("Dialog with ") + user.get_string(True) + "\n\n"
    dialog.data["public_indicator"] = 1
    dialog.data["category"] = category[1]
    dialog.data["page"] = 0

    menu_data = {
        "chat_member": member,
        "time_filters": access_settings.time_filters
    }

    bot_message = await dialog.send_message(game_creation_texts["punishment"], punishments, menu_data=menu_data)
    dialog.data["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)
    await message.delete()


@game_creation_router.callback_query(ButtonFilter(punishment))
async def select_punishment(callback: CallbackQuery, member: ChatMember, button: ButtonInstance, bot):
    await callback.answer()
    game = HiddenMinesGame(
        punishment_id=button.data["id"],
        is_opened_to_join=True,
        creator=member
    )

    game.get_random_2_by_2_field()

    await HiddenMinesGamePlayer(game=game, chat_member=member).asave()
    await game.asave()
    dialog = Dialog.create("hidden_mines_game", user_id=member.user_id, chat_id=member.chat_id, bot=bot)
    dialog.data["game_id"] = str(game.id)
    dialog.data["game_text"] = game.get_string()

    await dialog.send_message(hidden_mines_game_texts["game"], hidden_mines_field, menu_data={"game": game})
