import discord
from discord.ext import commands, tasks
import json
import datetime

TOKEN = x

TARGET_CHANNEL_ID = x
TRANSACTION_RECORD = {}
OPEN_TRANSACTIONS = {}
COOLDOWN = {}

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_user_base() -> dict:
    for i in range(3):
        try:
            with open("user_base.json", "r") as file:
                return json.load(file)
        except:
            pass
        
def save_user_base(user_base: dict) -> None:
    for i in range(3):
        try:
            with open("user_base.json", "w") as file:
                json.dump(user_base, file)
        except:
            pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found. Please mention a valid member.")
    else:
        raise error

@tasks.loop(seconds=1)
async def refill_aura():
    # refill aura every day at 0:00
    now = datetime.datetime.now()
    if now.hour == 0 and now.minute == 0 and now.second == 0:
        TRANSACTION_RECORD.clear()

        USER_BASE = load_user_base()

        for user_id in USER_BASE:
            refill_amount = 100 + USER_BASE[user_id][2] * 10
            USER_BASE[user_id][1] = refill_amount
            print(f"Refill Aura | User: {user_id} | Amount: {refill_amount} | Time: {now}")

        save_user_base(USER_BASE)

    # bonus aura refill every monday at 7:00
    if now.weekday() == 0 and now.hour == 7 and now.minute == 0 and now.second == 0:
        USER_BASE = load_user_base()

        for user_id in USER_BASE:
            bonus_amount = 500
            USER_BASE[user_id][1] += bonus_amount
            print(f"Refill Aura | User: {user_id} | Amount: {bonus_amount} | Time: {now}")

        save_user_base(USER_BASE)

@tasks.loop(seconds=1)
async def close_transactions():
    now = datetime.datetime.now()
    for user_id in OPEN_TRANSACTIONS:
        if now >= OPEN_TRANSACTIONS[user_id]["close_time"]:
            channel = bot.get_channel(TARGET_CHANNEL_ID)

            USER_BASE = load_user_base()

            participant_count = len(OPEN_TRANSACTIONS[user_id]) - 1

            if participant_count > 1:
                if len(set(OPEN_TRANSACTIONS[user_id].values())) == 1:
                    for transaction_user_id in OPEN_TRANSACTIONS[user_id]:
                        if transaction_user_id != "close_time":
                            amount = int(round(OPEN_TRANSACTIONS[user_id][transaction_user_id] / (participant_count)))
                            print(f"Transaction Payout | From: {transaction_user_id} | To: {user_id} | Amount: +{amount} | Time: {now}")
                else:
                    highest_bid = max(OPEN_TRANSACTIONS[user_id], key=OPEN_TRANSACTIONS[user_id].get)
                    for transaction_user_id in OPEN_TRANSACTIONS[user_id]:
                        if transaction_user_id != "close_time":
                            if transaction_user_id == highest_bid:
                                amount = int(round(OPEN_TRANSACTIONS[user_id][transaction_user_id] / (participant_count))) * 0.1 * participant_count        
                            else:
                                amount = int(round(OPEN_TRANSACTIONS[user_id][transaction_user_id] / (participant_count))) * 0.9        

                            USER_BASE[transaction_user_id][0] += amount

                            print(f"Transaction Payout | From: {transaction_user_id} | To: {user_id} | Amount: +{amount} | Time: {now}")
            else:
                await channel.send(f"Transaction Expired: Not enough participants for {channel.guild.get_member(int(user_id)).mention} loot.")
            save_user_base(USER_BASE)

            del OPEN_TRANSACTIONS[user_id]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    allowed_commands = ['!transfer', '!loot', '!balance', '!leaderboard', '!substitute', '!micro']

    if message.channel.id == TARGET_CHANNEL_ID and not any(message.content.startswith(command) for command in allowed_commands):
        await message.delete()
        print("Invalid command removed in channel {}: {}".format(message.channel.name, message.content))
    else:
        await bot.process_commands(message)

@bot.command()
async def transfer(ctx, member: discord.Member, amount: int):
    """Reagiert auf den Befehl !transfer @someone 500."""
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command cannot be used in DMs.")
        return
    
    if amount <= 0:
        await ctx.send("Amount must be a positive integer.")
        return

    USER_BASE = load_user_base()

    if str(ctx.author.id) not in USER_BASE:
        USER_BASE[str(ctx.author.id)] = [0, 100, 0]
    if str(member.id) not in USER_BASE:
        USER_BASE[str(member.id)] = [0, 100, 0]

    if ctx.author.id != member.id:
        if USER_BASE[str(ctx.author.id)][1] < amount:
            await ctx.send(f"Illegal: You only own {USER_BASE[str(ctx.author.id)][1]} aura.")
        else:
            USER_BASE[str(member.id)][0] += amount
            USER_BASE[str(ctx.author.id)][1] -= amount

            if str(ctx.author.id) not in TRANSACTION_RECORD:
                USER_BASE[str(ctx.author.id)][2] += 1
                TRANSACTION_RECORD[str(ctx.author.id)] = datetime.datetime.now()
                print(f"Transaction record created | User: {ctx.author.id} | Time: {TRANSACTION_RECORD[str(ctx.author.id)]}") 
            if amount >= 10 and (datetime.datetime.now() - TRANSACTION_RECORD[str(ctx.author.id)]).total_seconds() / 60 >= 10:
                USER_BASE[str(ctx.author.id)][2] += 1
                TRANSACTION_RECORD[str(ctx.author.id)] = datetime.datetime.now()
                print(f"Transaction record created | User: {ctx.author.id} | Time: {TRANSACTION_RECORD[str(ctx.author.id)]}") 

            save_user_base(USER_BASE)
            
            await ctx.send(f"Transaction: {ctx.author.mention} gives {member.mention} {amount} aura.")
            print(f"Transaction | From: {ctx.author.id} | To: {member.id} | Amount: +{amount} | Time: {datetime.datetime.now()}")
    else:
        await ctx.send("Illegal: You cannot give yourself aura.")

@bot.command()
async def loot(ctx, member: discord.Member, amount: int):
    """Reagiert auf den Befehl !loot @someone 500."""
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command cannot be used in DMs.")
        return
    
    if amount <= 0:
        await ctx.send("Amount must be a positive integer.")
        return
    
    USER_BASE = load_user_base()

    if str(ctx.author.id) not in USER_BASE:
        USER_BASE[str(ctx.author.id)] = [0, 100, 0]
    if str(member.id) not in USER_BASE:
        USER_BASE[str(member.id)] = [0, 100, 0]

    if ctx.author.id != member.id:
        if USER_BASE[str(member.id)][0]*0.7 < amount:
            await ctx.send(f"Illegal: That is more than 70% of {member.mention}'s wealth.")
        else:
            if str(member.id) not in OPEN_TRANSACTIONS:
                OPEN_TRANSACTIONS[str(member.id)] = {}
            
            if str(ctx.author.id) not in OPEN_TRANSACTIONS[str(member.id)]:
                OPEN_TRANSACTIONS[str(member.id)][str(ctx.author.id)] = amount
                if len(OPEN_TRANSACTIONS[str(member.id)]) == 1:
                    await ctx.send(f"Open Transaction: {ctx.author.mention} wants to take {member.mention} {amount} aura.\n*This transaction will close at {(datetime.datetime.now() + datetime.timedelta(minutes=3)).strftime('%H:%M:%S')}*")
                    OPEN_TRANSACTIONS[str(member.id)]["close_time"] = datetime.datetime.now() + datetime.timedelta(minutes=3)
                else:
                    await ctx.send(f"Participation: {ctx.author.mention} wants to take {member.mention} {amount} aura.")
            else:
                await ctx.send(f"Illegal: You have already participated in this transaction.")
    else:
        await ctx.send("Illegal: You cannot take aura from yourself.")

@bot.command()
async def balance(ctx, member: discord.Member = None):
    """Reagiert auf den Befehl !balance @someone."""
    USER_BASE = load_user_base()

    if member is None:
        member = ctx.author

    if str(member.id) not in USER_BASE:
        USER_BASE[str(member.id)] = [0, 100, 0]

    save_user_base(USER_BASE)

    await ctx.author.send(f"--> *{datetime.datetime.now().strftime('%H:%M:%S')}*\n{member.mention}'s **Balance**:\nProfile (Assets): {USER_BASE[str(member.id)][0]} aura\nWallet: {USER_BASE[str(member.id)][1]} aura\nTotal Networth: {USER_BASE[str(member.id)][0] + USER_BASE[str(member.id)][1]} aura")
    await ctx.message.delete()
    print(f"Balance Request | User: {ctx.author.id} | From: {member.id}")

@bot.command()
async def leaderboard(ctx):
    """Reagiert auf den Befehl !leaderboard."""
    USER_BASE = load_user_base()

    sorted_user_base = sorted(USER_BASE.items(), key=lambda x: x[1], reverse=True)

    leaderboard = f"--> *{datetime.datetime.now().strftime('%H:%M:%S')}*\n**Leaderboard**:\n"
    for i, (user_id, points) in enumerate(sorted_user_base):
        user = await bot.fetch_user(int(user_id))
        leaderboard += f"{i+1}. {user.name}: {points[0]} aura\n"

    await ctx.author.send(leaderboard)
    await ctx.message.delete()
    print(f"Leaderboard Request | User: {ctx.author.id}")

@bot.command()
async def micro(ctx, member: discord.Member):
    """Reagiert auf den Befehl !micro."""
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command cannot be used in DMs.")
        return
    
    if str(ctx.author.id) == str(member.id):
        await ctx.send("Illegal: You cannot take aura from yourself.")
    
    if str(ctx.author.id) not in COOLDOWN:
        COOLDOWN[str(ctx.author.id)] = datetime.datetime.now()
    else:
        if (datetime.datetime.now() - COOLDOWN[str(ctx.author.id)]).total_seconds() / 60 < 5:
            await ctx.send("Illegal: You are on cooldown for microtransactions.")
            return
        else:
            COOLDOWN[str(ctx.author.id)] = datetime.datetime.now()

    USER_BASE = load_user_base()

    if str(ctx.author.id) not in USER_BASE:
        USER_BASE[str(ctx.author.id)] = [0, 100, 0]

    if str(member.id) != str(ctx.author.id):
        amount = 1 if USER_BASE[str(member.id)][0] * 0.01 < 1 else int(round(USER_BASE[str(member.id)][0] * 0.01))
        USER_BASE[str(member.id)][0] -= amount
        USER_BASE[str(ctx.author.id)][1] += amount 

    save_user_base(USER_BASE)

    await ctx.send(f"Micro Transaction: {ctx.author.mention} takes {amount} (1%) of {member.mention}'s aura.")
    print(f"Microtransaction | User: {ctx.author.id} | From: {member.id} | Amount: +{amount} | Time: {datetime.datetime.now()}")

@bot.command()
async def substitute(ctx, amount: int):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command cannot be used in DMs.")
        return
    
    if amount <= 0:
        await ctx.send("Amount must be a positive integer.")
        return
    
    USER_BASE = load_user_base()
    
    if str(ctx.author.id) not in USER_BASE:
        USER_BASE[str(ctx.author.id)] = [0, 100, 0]

    USER_BASE[str(ctx.author.id)][0] += int(round(amount / 2))
    USER_BASE[str(ctx.author.id)][1] -= amount

    save_user_base(USER_BASE)

    await ctx.send(f"Substitution: {ctx.author.mention} converted {amount} aura into {int(round(amount/2))} aura worth of assests.")
    print(f"Substitution | User: {ctx.author.id} | Amount: {amount} | Converted: {int(round(amount/2))} | Time: {datetime.datetime.now()}")

@bot.event
async def on_ready():
    print(f"Exchange is Online | Time: {datetime.datetime.now()}")
    close_transactions.start()
    refill_aura.start()

bot.run(TOKEN)
