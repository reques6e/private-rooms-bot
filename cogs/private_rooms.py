from nextcord.ext import commands
from nextcord.ui import Button, View
import sqlite3
import nextcord
import datetime
from config import *

connection = sqlite3.connect('db/pr.db')
cursor = connection.cursor()


class DropdownOwn(nextcord.ui.Select):
    def __init__(self):
        selectOptions = []
        counter = 0
        for membs in private_voice.members:
            if membs != user:
                counter += 1
                selectOptions.append(nextcord.SelectOption(label=membs.display_name, description="Нажмите, чтобы назначить его владельцем комнаты", value=membs.id))
        super().__init__(placeholder="Выбрать участника", min_values=1,
                         max_values=1, options=selectOptions)

    async def callback(self, interaction: nextcord.Interaction):
        cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
        voiceid = cursor.fetchone()
        if voiceid is not None:
            private_voice = interaction.guild.get_channel(voiceid[0])
            if interaction.guild.get_member(int(self.values[0])) in private_voice.members:
                cursor.execute('UPDATE privates SET perms = {} WHERE perms = {}'.format(int(self.values[0]), interaction.user.id))
                connection.commit()
                await interaction.send("<@{}> назначен владельцем приватной комнаты!".format(int(self.values[0])), ephemeral=True)
                cursor.execute('UPDATE privates SET perms = {} WHERE ownerid = {}'.format(int(self.values[0]), interaction.user.id))
                connection.commit()
            else:
                await interaction.send("{}, извините, но <@{}> не находится в **приватной комнате**".format(interaction.user.mention, int(self.values[0])), ephemeral=True)


class DropdownAcc(nextcord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Выбрать участника (1-10)", min_values=1,
                         max_values=10)

    async def callback(self, interaction: nextcord.Interaction):
        cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
        voiceid = cursor.fetchone()
        private_voice = interaction.guild.get_channel(voiceid[0])
        overwrite = private_voice.overwrites
        mess = ''
        for fr_ow in self.values:
            check_on = overwrite.get(fr_ow)
            if check_on is None:
                overwrite.update({fr_ow: nextcord.PermissionOverwrite(connect=True)})
                await private_voice.edit(overwrites=overwrite)
                check_on = overwrite.get(fr_ow)
            if check_on == nextcord.PermissionOverwrite(connect=True):
                overwrite.update({fr_ow: nextcord.PermissionOverwrite(connect=False)})
                mess += '❌ {} отныне не может заходить в вашу приватную комнату!\n'.format(fr_ow.mention)
            elif check_on == nextcord.PermissionOverwrite(connect=False):
                overwrite.update({fr_ow: nextcord.PermissionOverwrite(connect=True)})
                mess += '✅ {} отныне может заходить в вашу приватную комнату!\n'.format(fr_ow.mention)
        await private_voice.edit(overwrites=overwrite)
        await acc_mes.edit(embed=embacc, view=None)
        try:
            await interaction.send(mess, ephemeral=True)
        except nextcord.errors.HTTPException:
            pass
        await acc_mes.edit(embed=embacc, view=DPVacc)
        cursor.execute("SELECT ownerid FROM privates WHERE ownerid = {}".format(interaction.user.id))
        check_own_id = cursor.fetchone()
        if check_own_id is None:
            cursor.execute('INSERT INTO privates(ownerid, voicename, voicelim, overwrites, voiceid, perms) VALUES ({}, "{}", {}, "{}", {}, {})'.format(interaction.user.id, interaction.user.display_name, private_voice.user_limit, overwrite, private_voice.id, private_voice.id))
            connection.commit()
        else:
            cursor.execute('UPDATE privates SET overwrites = "{}" WHERE ownerid = {}'.format(overwrite, interaction.user.id))
            connection.commit()


class DropdownKick(nextcord.ui.Select):
    def __init__(self):
        selectOptions = []
        counter = 0
        for membs in private_voice.members:
            if membs != user:
                counter += 1
                selectOptions.append(nextcord.SelectOption(label=membs.display_name, description="Нажмите, чтобы кикнуть данного пользователя из приватной комнаты", value=membs.id))
        super().__init__(placeholder="Выбрать участника", min_values=1,
                         max_values=1, options=selectOptions)

    async def callback(self, interaction: nextcord.Interaction):
        cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
        voiceid = cursor.fetchone()
        private_voice = interaction.guild.get_channel(voiceid[0])
        if interaction.guild.get_member(int(self.values[0])) in private_voice.members:
            await interaction.guild.get_member(int(self.values[0])).disconnect()
            await interaction.send("<@{}> был **кикнут** из **приватной комнаты**!".format(int(self.values[0])), ephemeral=True)
            await kick_msg.edit(embed=embkick, view=None)
            await kick_msg.edit(embed=embkick, view=DPVkick)
        else:
            await interaction.send("{}, извините, но <@{}> не находится в **приватной комнате**".format(interaction.user.mention, int(self.values[0])), ephemeral=True)


class DropdownMute_True(nextcord.ui.Select):
    def __init__(self):
        selectOptions = []
        counter = 0
        for membs in private_voice.members:
            if membs != user:
                counter += 1
                selectOptions.append(nextcord.SelectOption(label=membs.display_name, description="Нажмите, чтобы замутить/размутить этого пользователя", value=membs.id))
        super().__init__(placeholder="Выбрать участника", min_values=1,
                         max_values=1, options=selectOptions)

    async def callback(self, interaction: nextcord.Interaction):
        cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
        voiceid = cursor.fetchone()
        private_voice = interaction.guild.get_channel(voiceid[0])
        if interaction.guild.get_member(int(self.values[0])) in private_voice.members:
            if interaction.guild.get_member(int(self.values[0])).voice.mute is False:
                await interaction.guild.get_member(int(self.values[0])).edit(mute=True)
                await interaction.send("❌ <@{}> был **замучен** в данной **приватной комнате**".format(int(self.values[0])), ephemeral=True)
            await mute_mes.edit(embed=embmute, view=None)
            await mute_mes.edit(embed=embmute, view=DPVmute)
        else:
            await interaction.send("{}, извините, но <@{}> не находится в **приватной комнате**".format(interaction.user.mention, int(self.values[0])), ephemeral=True)

class DropdownMute_False(nextcord.ui.Select):
    def __init__(self):
        selectOptions = []
        counter = 0
        for membs in private_voice.members:
            if membs != user:
                counter += 1
                selectOptions.append(nextcord.SelectOption(label=membs.display_name, description="Нажмите, чтобы замутить/размутить этого пользователя", value=membs.id))
        super().__init__(placeholder="Выбрать участника", min_values=1,
                         max_values=1, options=selectOptions)

    async def callback(self, interaction: nextcord.Interaction):
        cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
        voiceid = cursor.fetchone()
        private_voice = interaction.guild.get_channel(voiceid[0])
        if interaction.guild.get_member(int(self.values[0])) in private_voice.members:
            if interaction.guild.get_member(int(self.values[0])).voice.mute is True:
                await interaction.guild.get_member(int(self.values[0])).edit(mute=False)
                await interaction.send("✅ <@{}> был **размучен** в данной **приватной комнате**".format(int(self.values[0])), ephemeral=True)
            await mute_mes.edit(embed=embmute, view=None)
            await mute_mes.edit(embed=embmute, view=DPVmute)
        else:
            await interaction.send("{}, извините, но <@{}> не находится в **приватной комнате**".format(interaction.user.mention, int(self.values[0])), ephemeral=True)


class EditLim(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Изменение лимита")
        self.edlim = nextcord.ui.TextInput(
            label="Лимит", placeholder="Максимально количество мест: 99", min_length=1, max_length=2, required=True)
        self.add_item(self.edlim)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
        voiceid = cursor.fetchone()
        private_voice = interaction.guild.get_channel(voiceid[0])
        cursor.execute("SELECT ownerid FROM privates WHERE ownerid = {}".format(interaction.user.id))
        check_own_id = cursor.fetchone()
        if check_own_id is None:
            cursor.execute('INSERT INTO privates(ownerid, voicename, voicelim, overwrites, voiceid, perms) VALUES ({}, "{}", {}, "{}", {}, {})'.format(interaction.user.id, interaction.user.display_name, self.edlim.value, private_voice.overwrites, private_voice.id, private_voice.id))
            connection.commit()
        else:
            cursor.execute("UPDATE privates SET voicelim = {} WHERE ownerid = {}".format(self.edlim.value, interaction.user.id))
            connection.commit()
        await private_voice.edit(user_limit=self.edlim.value)


class EditName(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Изменение названия")
        self.edname = nextcord.ui.TextInput(
            label="Название", placeholder="Максимально количество символов: 100", min_length=1, max_length=100, required=True)
        self.add_item(self.edname)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
        voiceid = cursor.fetchone()
        private_voice = interaction.guild.get_channel(voiceid[0])
        cursor.execute("SELECT ownerid FROM privates WHERE ownerid = {}".format(interaction.user.id))
        check_own_id = cursor.fetchone()
        if check_own_id is None:
            cursor.execute('INSERT INTO privates(ownerid, voicename, voicelim, overwrites, voiceid, perms) VALUES ({}, "{}", {}, "{}", {}, {})'.format(interaction.user.id, self.edname.value, private_voice.user_limit, private_voice.overwrites, private_voice.id, private_voice.id))
            connection.commit()
        else:
            cursor.execute("UPDATE privates SET voicename = '{}' WHERE ownerid = {}".format(self.edname.value, interaction.user.id))
            connection.commit()
        await private_voice.edit(name=self.edname.value)


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Private Rooms - work")
        cursor.execute("""CREATE TABLE IF NOT EXISTS privates(
            ownerid BIGINT,
            voicename TEXT,
            voicelim INT,
            overwrites TEXT,
            voiceid BIGINT,
            perms BIGINT);
        """)
        connection.commit()
        guild = self.bot.get_guild(guild_id)
        strt_send = guild.get_channel(private_control_id)
        emb = nextcord.Embed(title='Управление приватными комнатами',
                             description='> Жми следующие кнопки, чтобы настроить свою комнату',
                             color=nextcord.Colour.from_rgb(47, 49, 54))
        emb.add_field(name='ㅤ', 
                      value=f'{emoji1} — Передать владельца\n{emoji2} — изменить лимит\n{emoji3} — закрыть доступ\n{emoji4} — открыть доступ\n{emoji5} — размутить')
        emb.add_field(name='ㅤ',
                      value=f'{emoji6} — замутить\n{emoji7} — скрыть/открыть комнату\n{emoji8} — закрыть/открыть доступ\n{emoji9} — изменить название\n{emoji10} — выгнать участника')

        new_ownr = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji1}')
        new_lim = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji2}',
                        row=2)
        opn_clsd_true = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji3}')
        opn_clsd_false = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji4}',
                        row=2)
        micro_no_false = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji5}')
        micro_no_true = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji6}',
                        row=2)
        hidden = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji7}')
        kick_memb = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji8}',
                        row=2)
        access = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji9}',
                        row=2)
        new_name = Button(style=nextcord.ButtonStyle.grey,
                        emoji=f'{emoji10}')

        async def new_ownr_callback(interaction: nextcord.Interaction):
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            global user
            user = interaction.user
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                emb = nextcord.Embed(title='Настройки приватной комнаты:',
                                     description='Выберите пользователя, которому желаете передать права владельца приватной комнаты.',
                                     color=nextcord.Colour.from_rgb(47, 49, 54))
                emb.timestamp = datetime.datetime.now()
                emb.add_field(name='Текущие настройки:', value='Владелец: {}\nНазвание: **{}** ({})\nЛимит: **{}**\nБитрейт: **{}**'.format(interaction.guild.get_member(ownerid[1]).mention, private_voice.name, private_voice.mention, private_voice.user_limit, private_voice.bitrate))
                try:
                    DPVown = View(timeout=None)
                    DPVown.add_item(DropdownOwn())
                    await interaction.send(embed=emb, view=DPVown, ephemeral=True)
                except nextcord.errors.HTTPException:
                    await interaction.send('{}, извините, но у вас нет пользователей для переачи им прав'.format(interaction.user.mention), ephemeral=True)
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def access_callback(interaction: nextcord.Interaction):
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            global user
            user = interaction.user
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                global embacc
                embacc = nextcord.Embed(title='Настройки приватной комнаты:',
                                     description='Выберите пользователя, которому желаете заблокировать/открыть доступ приватной комнаты.',
                                     color=nextcord.Colour.from_rgb(47, 49, 54))
                embacc.timestamp = datetime.datetime.now()
                embacc.add_field(name='Текущие настройки:', value='Владелец: {}\nНазвание: **{}** ({})\nЛимит: **{}**\nБитрейт: **{}**'.format(interaction.guild.get_member(ownerid[1]).mention, private_voice.name, private_voice.mention, private_voice.user_limit, private_voice.bitrate))
                global DPVacc
                DPVacc = View(timeout=None)
                DPVacc.add_item(DropdownAcc())
                global acc_mes
                acc_mes = await interaction.send(embed=embacc, view=DPVacc, ephemeral=True)
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def new_lim_callback(interaction: nextcord.Interaction):
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                await interaction.response.send_modal(EditLim())
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def opn_clsd_false_callback(interaction: nextcord.Interaction):
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                overwrite = private_voice.overwrites
                if private_voice.permissions_for(private_voice.guild.default_role).connect is True:
                    overwrite.update({private_voice.guild.default_role: nextcord.PermissionOverwrite(connect=False)})
                    await private_voice.edit(overwrites=overwrite)
                    await interaction.send("❌ Вы **закрыли** свою комнату для **всех** пользователей", ephemeral=True)
                
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def opn_clsd_true_callback(interaction: nextcord.Interaction):
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                overwrite = private_voice.overwrites
                if private_voice.permissions_for(private_voice.guild.default_role).connect is False:
                    overwrite.update({private_voice.guild.default_role: nextcord.PermissionOverwrite(connect=True)})
                    await private_voice.edit(overwrites=overwrite)
                    await interaction.send("✅ Вы **открыли** свою комнату для **всех** пользователей", ephemeral=True)
                
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def new_name_callback(interaction: nextcord.Interaction):
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                await interaction.response.send_modal(EditName())
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def hidden_callback(interaction: nextcord.Interaction):
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                overwrite = private_voice.overwrites
                if private_voice.permissions_for(private_voice.guild.default_role).view_channel is True:
                    overwrite.update({private_voice.guild.default_role: nextcord.PermissionOverwrite(view_channel=False)})
                    await private_voice.edit(overwrites=overwrite)
                    await interaction.send("❌ Вы **скрыли** свою комнату для **всех** пользователей", ephemeral=True)
                else:
                    overwrite.update({private_voice.guild.default_role: nextcord.PermissionOverwrite(view_channel=True)})
                    await private_voice.edit(overwrites=overwrite)
                    await interaction.send("✅ Вы **раскрыли** свою комнату для **всех** пользователей", ephemeral=True)
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)


        async def kick_memb_callback(interaction: nextcord.Interaction):
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            global user
            user = interaction.user
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                global embkick
                embkick = nextcord.Embed(title='Настройки приватной комнаты:',
                                     description='Выберите пользователя, которого желаете кикнуть из приватной комнаты.',
                                     color=nextcord.Colour.from_rgb(47, 49, 54))
                embkick.timestamp = datetime.datetime.now()
                embkick.add_field(name='Текущие настройки:', value='Владелец: {}\nНазвание: **{}** ({})\nЛимит: **{}**\nБитрейт: **{}**'.format(interaction.guild.get_member(ownerid[1]).mention, private_voice.name, private_voice.mention, private_voice.user_limit, private_voice.bitrate))
                try:
                    global DPVkick
                    DPVkick = View(timeout=None)
                    DPVkick.add_item(DropdownKick())
                    global kick_msg
                    kick_msg = await interaction.send(embed=embkick, view=DPVkick, ephemeral=True)
                except nextcord.errors.HTTPException:
                    await interaction.send('{}, извините, но у вас нет пользователей для того чтобы **кикнуть** кого-то из них'.format(interaction.user.mention), ephemeral=True)
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def micro_no_true_callback(interaction: nextcord.Interaction):
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            global user
            user = interaction.user
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                global embmute
                embmute = nextcord.Embed(title='Настройки приватной комнаты:',
                                     description='Выберите пользователя, которого желаете замутить в приватной комнаты.',
                                     color=nextcord.Colour.from_rgb(47, 49, 54))
                embmute.timestamp = datetime.datetime.now()
                embmute.add_field(name='Текущие настройки:', value='Владелец: {}\nНазвание: **{}** ({})\nЛимит: **{}**\nБитрейт: **{}**'.format(interaction.guild.get_member(ownerid[1]).mention, private_voice.name, private_voice.mention, private_voice.user_limit, private_voice.bitrate))
                try:
                    global DPVmute
                    DPVmute = View(timeout=None)
                    DPVmute.add_item(DropdownMute_True())
                    global mute_mes
                    mute_mes = await interaction.send(embed=embmute, view=DPVmute, ephemeral=True)
                except nextcord.errors.HTTPException:
                    await interaction.send('{}, извините, но у вас нет пользователей для того чтобы **замутить** кого-то из них'.format(interaction.user.mention), ephemeral=True)
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def micro_no_false_callback(interaction: nextcord.Interaction):
            cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(interaction.user.id))
            voiceid = cursor.fetchone()
            if voiceid is None:
                voiceid = [0]
            global private_voice
            private_voice = interaction.guild.get_channel(voiceid[0])
            global user
            user = interaction.user
            cursor.execute(
                "SELECT voiceid, perms FROM privates WHERE perms = {}".format(interaction.user.id))
            ownerid = cursor.fetchone()
            if ownerid is None:
                ownerid = [0, 0]
            if interaction.user.id == ownerid[1] and interaction.user in interaction.guild.get_channel(ownerid[0]).members:
                global embmute
                embmute = nextcord.Embed(title='Настройки приватной комнаты:',
                                     description='Выберите пользователя, которого желаете размьютить в приватной комнаты.',
                                     color=nextcord.Colour.from_rgb(47, 49, 54))
                embmute.timestamp = datetime.datetime.now()
                embmute.add_field(name='Текущие настройки:', value='Владелец: {}\nНазвание: **{}** ({})\nЛимит: **{}**\nБитрейт: **{}**'.format(interaction.guild.get_member(ownerid[1]).mention, private_voice.name, private_voice.mention, private_voice.user_limit, private_voice.bitrate))
                try:
                    global DPVmute
                    DPVmute = View(timeout=None)
                    DPVmute.add_item(DropdownMute_False())
                    global mute_mes
                    mute_mes = await interaction.send(embed=embmute, view=DPVmute, ephemeral=True)
                except nextcord.errors.HTTPException:
                    await interaction.send('{}, извините, но у вас нет пользователей для того чтобы **размьютить** кого-то из них'.format(interaction.user.mention), ephemeral=True)
            else:
                await interaction.send('{}, извините, но вы не являетесь **владельцем приватной комнаты**!'.format(interaction.user.mention), ephemeral=True)

        async def author_info_callback(interaction: nextcord.Interaction):
            await interaction.send('Хз.', ephemeral=True)

        new_ownr.callback = new_ownr_callback
        access.callback = access_callback
        new_lim.callback = new_lim_callback
        opn_clsd_true.callback = opn_clsd_true_callback
        opn_clsd_false.callback = opn_clsd_false_callback 
        new_name.callback = new_name_callback
        hidden.callback = hidden_callback 
        kick_memb.callback = kick_memb_callback
        micro_no_true.callback = micro_no_true_callback
        micro_no_false.callback = micro_no_false_callback
        view = View(timeout=None)
        view.add_item(new_ownr)
        view.add_item(new_lim)
        view.add_item(opn_clsd_true)
        view.add_item(opn_clsd_false)
        view.add_item(micro_no_true)
        view.add_item(micro_no_false)
        view.add_item(hidden)
        view.add_item(access)
        view.add_item(kick_memb)
        view.add_item(new_name)

        m = [message async for message in strt_send.history(limit=1)]
        ch_channel = self.bot.get_channel(private_control_id)
        try:
            message = await ch_channel.fetch_message(create_private_chan_id)
            await message.edit(embed=emb, view=view)
        except:
            await strt_send.send(embed=emb, view=view)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
        cursor.execute("SELECT voiceid FROM privates WHERE perms = {}".format(member.id))
        voiceid = cursor.fetchone()
        cursor.execute("SELECT voicename, voicelim, overwrites FROM privates WHERE ownerid = {}".format(member.id))
        setting = cursor.fetchone()
        if voiceid is None:
            voiceid = [0]
        private_voice = member.guild.get_channel(voiceid[0])
        if after.channel is not None and member.voice.channel.id == create_private_chan_id and member.voice.channel is not None:
            if setting is not None:
                channel2 = await member.guild.create_voice_channel(name=setting[0], category=after.channel.category, user_limit=setting[1], overwrites={member: nextcord.PermissionOverwrite(connect=True), member.guild.default_role: nextcord.PermissionOverwrite(connect=True, view_channel=True)})
            else:
                channel2 = await member.guild.create_voice_channel(name=member.display_name, category=after.channel.category, user_limit=2, overwrites={member: nextcord.PermissionOverwrite(connect=True), member.guild.default_role: nextcord.PermissionOverwrite(connect=True, view_channel=True)})
            cursor.execute("SELECT ownerid FROM privates WHERE ownerid = {}".format(member.id))
            check_room = cursor.fetchone()
            if check_room is None:
                cursor.execute('INSERT INTO privates(ownerid, voicename, voicelim, overwrites, voiceid, perms) VALUES ({}, "{}", {}, "{}", {}, {})'.format(member.id, channel2.name, channel2.user_limit, channel2.overwrites, channel2.id, member.id))
                connection.commit()
            else:
                cursor.execute("UPDATE privates SET perms = {0} WHERE ownerid = {0}".format(check_room[0]))
                connection.commit()
                cursor.execute("UPDATE privates SET voiceid = {} WHERE ownerid = {}".format(channel2.id, check_room[0]))
                connection.commit()
            await member.move_to(channel2)
        if private_voice is not None:
            if len(private_voice.members) == 0:
                await private_voice.delete()
        if before.channel is not None and before.channel == private_voice and after.channel != private_voice:
            if len(private_voice.members) != 0:
                cursor.execute('UPDATE privates SET perms = {} WHERE voiceid = {}'.format(private_voice.members[0].id, private_voice.id))
                connection.commit()
            else:
                cursor.execute("UPDATE privates SET perms = Null WHERE voiceid = {}".format(private_voice.id))
                connection.commit()
            
    # @nextcord.slash_command(name='say', description='Оставить коментарий')
    # async def sdvsdfsdsdfdsfds(self, interaction: nextcord.Interaction):
    #     ch = self.bot.get_channel(1180419074472292382)
    #     await ch.send('Voice')

def setup(bot):
    bot.add_cog(Voice(bot))
