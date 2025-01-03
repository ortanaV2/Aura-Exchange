import discord
from discord.ext import commands, tasks
import json
import datetime
from cryptography.fernet import Fernet
import random

TOKEN = x

TARGET_CHANNEL_ID = x
TRANSACTION_RECORD = {}
OPEN_TRANSACTIONS = {}
COOLDOWN = {}

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

key = Fernet.generate_key()
CIPHER_SUITE = Fernet(key)

def load_user_base() -> dict:
    for i in range(3):
        try:
            with open("user_base.cac", "rb") as file:
                encrypted_data = file.read()
                decrypted_data = CIPHER_SUITE.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode('utf-8'))
        except:
            pass

def save_user_base(user_base: dict) -> None:
    for i in range(3):
        try:
            with open("user_base.cac", "wb") as file:
                data = json.dumps(user_base).encode('utf-8')
                encrypted_data = CIPHER_SUITE.encrypt(data)
                file.write(encrypted_data)
        except:
            pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found. Please mention a valid member.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument. Please provide all necessary arguments")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument. Please provide a valid argument.")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("Invalid amount. Please enter a valid integer.")
    elif isinstance(error, commands.CommandNotFound):
        print("Invalid command removed.")
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
            USER_BASE[user_id][1] += refill_amount
            print(f"Refill Aura | User: {user_id} | Amount: {refill_amount} | Time: {now}")

        save_user_base(USER_BASE)

    # bonus aura refill every monday at 7:00
    if now.weekday() == 0 and now.hour == 7 and now.minute == 0 and now.second == 0:
        USER_BASE = load_user_base()

        for user_id in USER_BASE:
            if USER_BASE[user_id][0] == max([user[0] for user in USER_BASE.values()]):
                bonus_amount = int(round(500 + USER_BASE[user_id][0] * 0.5))
                profile_bonus = USER_BASE[user_id][1] * 0.5
                USER_BASE[user_id][0] += profile_bonus
            else:
                bonus_amount = 500
            USER_BASE[user_id][1] += bonus_amount
            print(f"Refill Aura | User: {user_id} | Amount: {bonus_amount} | Time: {now}")

        save_user_base(USER_BASE)

@tasks.loop(seconds=1)
async def close_transactions():
        now = datetime.datetime.now()

        for auction_id in list(OPEN_TRANSACTIONS):
            if now >= OPEN_TRANSACTIONS[auction_id]["close_time"]:
                USER_BASE = load_user_base()

                if str(OPEN_TRANSACTIONS[auction_id]["member_id"]) not in USER_BASE:
                    USER_BASE[str(OPEN_TRANSACTIONS[auction_id]["member_id"])] = [0, 100, 0]

                bids = list(OPEN_TRANSACTIONS[auction_id]["participants"].values())
                bids.sort()

                if len(bids) < 3:
                    channel = bot.get_channel(TARGET_CHANNEL_ID)
                    await channel.send(f"The `{auction_id}` auction has expired due to insufficient participants. The bids will be refunded.")
                    for participant_id in OPEN_TRANSACTIONS[auction_id]["participants"]:
                        USER_BASE[str(participant_id)][1] += OPEN_TRANSACTIONS[auction_id]["participants"][str(participant_id)]
                        save_user_base(USER_BASE)

                        user = bot.get_user(int(participant_id))
                        if user is None:
                            user = await bot.fetch_user(int(participant_id))
                        if user:
                            await user.send(f"**Auction Result**: You bid {OPEN_TRANSACTIONS[auction_id]['participants'][str(participant_id)]} aura on the `{auction_id}` auction. The bid has been refunded.\n*Participants: {len(bids)}*")
                        else:
                            print(f"User with ID {participant_id} not found.")
                        print(f"Refund Transaction | User: {participant_id} | Amount: +{OPEN_TRANSACTIONS[auction_id]['participants'][str(participant_id)]} | Time: {now}")
                else:
                    min_bid = min(bids)
                    max_bid = max(bids)
                    for participant_id in OPEN_TRANSACTIONS[auction_id]["participants"]:
                        if str(participant_id) not in USER_BASE:
                            USER_BASE[str(participant_id)] = [0, 100, 0]
                        
                        bid_amount = OPEN_TRANSACTIONS[auction_id]["participants"][str(participant_id)]
                        sets_amount = len(set(bids))

                        if sets_amount == 1:
                            profit = int(round(bid_amount / len(bids)))
                            position = "Average "
                            USER_BASE[str(participant_id)][0] += profit
                        else:    
                            position = ""
                            if OPEN_TRANSACTIONS[auction_id]["participants"][str(participant_id)] == min_bid:
                                amount_gab = bids[1] - min_bid
                                profit = bid_amount - amount_gab
                                position += "Minimum "
                                USER_BASE[str(participant_id)][0] += profit
                            elif OPEN_TRANSACTIONS[auction_id]["participants"][str(participant_id)] == max_bid:
                                amount_gab = max_bid - bids[-2]
                                profit = bid_amount - amount_gab
                                position += "Maximum "
                                USER_BASE[str(participant_id)][0] += profit
                            else:
                                profit = int(round(bid_amount + max_bid / (len(bids) - 2)))
                                position += "Average "
                                USER_BASE[str(participant_id)][0] += profit
                        
                        save_user_base(USER_BASE)

                        user = bot.get_user(int(participant_id))
                        if user is None:
                            user = await bot.fetch_user(int(participant_id))
                        if user:
                            await user.send(f"**Auction Result**: You bid {bid_amount} aura on the `{auction_id}` auction. The return is {profit} aura.\n*Position: {position}\tParticipants: {len(bids)}*")
                        else:
                            print(f"User with ID {participant_id} not found.")

                        print(f"Payout Transaction | From: {participant_id} | To: {OPEN_TRANSACTIONS[auction_id]['member_id']} | Amount: {profit} | Time: {now}")
                    
                    USER_BASE[str(OPEN_TRANSACTIONS[auction_id]["member_id"])][0] -= max_bid
                    print(f"Auction Transaction | User: {OPEN_TRANSACTIONS[auction_id]['member_id']} | Amount: -{max_bid} | Time: {now}")
                    save_user_base(USER_BASE)

                    member = bot.get_user(OPEN_TRANSACTIONS[auction_id]["member_id"])
                    if member is None:
                        member = await bot.fetch_user(OPEN_TRANSACTIONS[auction_id]["member_id"])
                    if member:
                        await member.send(f"**Auction Result**: You were looted for {max_bid} aura in the `{auction_id}` auction.\n*Participants: {len(bids)}*")

                del OPEN_TRANSACTIONS[auction_id]
                print(f"Auction Closed | ID: {auction_id} | Time: {now}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    allowed_commands = ['!transfer', '!loot', '!balance', '!leaderboard', '!substitute', '!micro', '!auction']

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
                print(f"Transaction Record Created | User: {ctx.author.id} | Time: {TRANSACTION_RECORD[str(ctx.author.id)]}") 
            if amount >= 10 and (datetime.datetime.now() - TRANSACTION_RECORD[str(ctx.author.id)]).total_seconds() / 60 >= 10:
                USER_BASE[str(ctx.author.id)][2] += 1
                TRANSACTION_RECORD[str(ctx.author.id)] = datetime.datetime.now()
                print(f"Transaction Record Created | User: {ctx.author.id} | Time: {TRANSACTION_RECORD[str(ctx.author.id)]}") 

            save_user_base(USER_BASE)
            
            await ctx.send(f"**Transaction**: {ctx.author.mention} gives {member.mention} {amount} aura.")
            print(f"Transaction | From: {ctx.author.id} | To: {member.id} | Amount: +{amount} | Time: {datetime.datetime.now()}")
    else:
        await ctx.send("Illegal: You cannot give yourself aura.")

@bot.command()
async def loot(ctx, auction_id, amount: int):
    """Reagiert auf den Befehl !loot @someone 500."""

    if auction_id not in OPEN_TRANSACTIONS:
        await ctx.send("Auction not found.")
        return
    
    if amount <= 0:
        await ctx.send("Amount must be a positive integer.")
        return
    
    USER_BASE = load_user_base()

    if str(ctx.author.id) not in USER_BASE:
        USER_BASE[str(ctx.author.id)] = [0, 100, 0]
    
    if ctx.author.id != OPEN_TRANSACTIONS[str(auction_id)]["member_id"]:
        if USER_BASE[str(OPEN_TRANSACTIONS[str(auction_id)]["member_id"])][0]*0.5 < amount:
            await ctx.send(f"Illegal: You cannot loot more than 50% of the target's assets.")
        elif USER_BASE[str(ctx.author.id)][1] < amount:
            await ctx.send(f"Illegal: You cannot afford such a high bid.")
        else:
            if str(ctx.author.id) not in OPEN_TRANSACTIONS[str(auction_id)]["participants"]:
                USER_BASE[str(ctx.author.id)][1] -= amount
                OPEN_TRANSACTIONS[str(auction_id)]["participants"][str(ctx.author.id)] = amount
                await ctx.send(f"**Participation**: {ctx.author.mention} bids {amount} aura.")
                print(f"Participation | User: {ctx.author.id} | Amount: -{amount} | Time: {datetime.datetime.now()}")
                save_user_base(USER_BASE)
            else:
                await ctx.send(f"Illegal: You have already participated in this transaction.")
    else:
        await ctx.send("Illegal: You cannot take aura from yourself.")

@bot.command()
async def auction(ctx, member: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command cannot be used in DMs.")
        return
    
    USER_BASE = load_user_base()

    if str(ctx.author.id) not in USER_BASE:
        USER_BASE[str(ctx.author.id)] = [0, 100, 0]

    if str(member.id) not in USER_BASE:
        USER_BASE[str(member.id)] = [0, 100, 0]

    save_user_base(USER_BASE)

    for retry in range(50):
        auction_id = ''.join(random.choices("123456789ABCDEFGHIJKLMNPQRSTUVWXYZ", k=3))
        if auction_id not in OPEN_TRANSACTIONS:
            break
        
    if any(member.id == OPEN_TRANSACTIONS[auction_id]["member_id"] for auction_id in OPEN_TRANSACTIONS):
        await ctx.send("Auction already in progress.")
    else:
        expire_time = 3  # minutes 
        OPEN_TRANSACTIONS[str(auction_id)] = {"member_id": member.id, "participants": {}, "close_time": datetime.datetime.now() + datetime.timedelta(minutes=expire_time)}
        await ctx.send(f"**Auction**: {ctx.author.mention} started an auction on {member.mention}. The loot key is `{auction_id}`.\n*This transaction will close at {(datetime.datetime.now() + datetime.timedelta(minutes=expire_time)).strftime('%H:%M:%S')}*")
        print(f"Auction | User: {ctx.author.id} | From: {member.id} | Auction ID: {auction_id} | Time: {datetime.datetime.now()}")

@bot.command()
async def balance(ctx, member: discord.Member = None):
    """Reagiert auf den Befehl !balance @someone."""
    USER_BASE = load_user_base()

    if member is None:
        member = ctx.author

    if str(member.id) not in USER_BASE:
        USER_BASE[str(member.id)] = [0, 100, 0]

    save_user_base(USER_BASE)

    await ctx.author.send(f"{member.mention}'s **Balance**:\nProfile (Assets): {USER_BASE[str(member.id)][0]} aura\nWallet: {USER_BASE[str(member.id)][1]} aura\nTotal Networth: {USER_BASE[str(member.id)][0] + USER_BASE[str(member.id)][1]} aura")
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.message.delete()
    print(f"Balance Request | User: {ctx.author.id} | From: {member.id}")

@bot.command()
async def leaderboard(ctx):
    """Reagiert auf den Befehl !leaderboard."""
    USER_BASE = load_user_base()

    sorted_user_base = sorted(USER_BASE.items(), key=lambda x: x[1], reverse=True)

    leaderboard = f"**Leaderboard**:\n"
    for i, (user_id, points) in enumerate(sorted_user_base):
        user = await bot.fetch_user(int(user_id))
        leaderboard += f"{i+1}. {user.name}: {points[0]} aura\n"

    await ctx.author.send(leaderboard)
    if not isinstance(ctx.channel, discord.DMChannel):
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

    if str(member.id) not in USER_BASE:
        USER_BASE[str(member.id)] = [0, 100, 0]

    if str(member.id) != str(ctx.author.id):
        amount = 1 if USER_BASE[str(member.id)][0] * 0.01 < 1 else int(round(USER_BASE[str(member.id)][0] * 0.01))
        USER_BASE[str(member.id)][0] -= amount
        USER_BASE[str(ctx.author.id)][1] += amount 

    save_user_base(USER_BASE)

    await ctx.send(f"**Micro Transaction**: {ctx.author.mention} takes {amount} (1%) of {member.mention}'s aura.")
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

    if amount > USER_BASE[str(ctx.author.id)][1]:
        await ctx.send(f"Illegal: You only own {USER_BASE[str(ctx.author.id)][1]} aura.")
        return
    else:
        USER_BASE[str(ctx.author.id)][0] += int(round(amount / 2))
        USER_BASE[str(ctx.author.id)][1] -= amount

        save_user_base(USER_BASE)

        await ctx.send(f"**Substitution**: {ctx.author.mention} converted {amount} aura into {int(round(amount/2))} aura worth of assests.")
        print(f"Substitution | User: {ctx.author.id} | Amount: {amount} | Converted: {int(round(amount/2))} | Time: {datetime.datetime.now()}")

@bot.event
async def on_ready():
    initial_user_base = {}

    data = json.dumps(initial_user_base).encode('utf-8')
    encrypted_data = CIPHER_SUITE.encrypt(data)

    with open("user_base.cac", "wb") as file:
        file.write(encrypted_data)

    print(f"Exchange is Online | Time: {datetime.datetime.now()}")

    close_transactions.start()
    refill_aura.start()

bot.run(TOKEN)
