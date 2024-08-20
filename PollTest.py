#        -----------TODO-----------
# ________________________________________
#
# HAVE BOT GENERATE A MATPLOTLIB BAR GRAPH WITH THE POLL RESULTS AND
# SEND IT AS THE RESULTS MESSAGE
# ________________________________________
#
# FIX AUTO DAILY POLL
# ________________________________________
#
# Allow user to edit the poll they created. 
# ________________________________________
#
# Add colored embed around the message.
# ________________________________________



# Import necessary modules
import discord
import asyncio
import re
import random
import requests

# Set up Discord client and intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Initialize variables
polls = {}
number_to_emoji = {
    '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣',
    '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟'
}
previous_polls = []


# Event: Bot is ready
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    #await send_daily_poll() **************FIX THIS**************

# Event: Message received
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!poll help'):
        await message.channel.send(
            '**To create a poll, use the command:** `!poll {question}: ' +
            '{option 1}, {option 2}...{option n}; {closing time (in minutes)}`\n' +
            '**Example:** `!poll What is your favorite color?: Red, Green, Blue, Yellow; 4`'
        )
    elif message.content.startswith('!poll delete'):
        pass
    elif message.content.startswith('!polls'):
        if message.content == '!polls':
            await display_polls(message.channel, 0)
        elif message.content == '!polls next':
            await display_polls(message.channel, 5)
    elif message.content.startswith('!poll'):
        # Extract the poll question, options, and closing time from the message
        match = re.match(r'!poll (.+): (.+); (\d+)', message.content)

        if not match:
            await message.channel.send(
                'Invalid poll format. Please use the following format: '
                '`!poll {question}: (option 1), (option 2)...etc; closing time: (time)`'
            )
            return

        question = match.group(1)
        options = [option.strip() for option in match.group(2).split(',')]
        closing_time = int(match.group(3))

        # Create the poll dictionary and add it to the polls list
        poll = {
            'question': question,
            'options': options,
            'closing_time': closing_time,
            'votes': {option: 0 for option in options}
        }
        polls[message.channel.id] = poll

        # Send the poll message and add number reactions
        poll_message = await message.channel.send(create_poll_message(poll))
        for i in range(len(options)):
            await poll_message.add_reaction(f'{i + 1}\N{combining enclosing keycap}')

# Close a poll
async def close_poll(poll_message, poll):
    # Calculate the poll results and send them in a message
    results_message = create_results_message(poll)
    most_popular_option = get_most_popular_option(poll)
    results_message += f"\n\nThe most popular option was: {most_popular_option}"
    await poll_message.channel.send(results_message)

    # Remove the poll from the polls list
    del polls[poll_message.channel.id]
    await poll_message.delete()

# Create the poll message text
def create_poll_message(poll):
    options_text = ""
    for i in range(len(poll['options'])):
        option_text = poll['options'][i]
        options_text += f"{number_to_emoji[str(i + 1)]} *{option_text}*\n"

    poll_message = f'**Question:** {poll["question"]}:\n{options_text}\n'
    return poll_message

# Create the results message text
def create_results_message(poll):
    total_votes = sum(poll['votes'].values())
    results_text = '\n'.join(
        [f'{number_to_emoji[str(i + 1)]} {option}: {poll["votes"][option]} votes ({poll["votes"][option] / total_votes * 100:.1f}% of total)'
         for i, option in enumerate(poll['options'])])
    results_message = f'**A POLL CLOSED, HERE ARE THE RESULTS:** \n{poll["question"]}:\n{results_text}'
    return results_message

# Find the option with the highest vote count
def get_most_popular_option(poll):
    max_votes = max(poll['votes'].values())
    most_popular_options = [option for option, votes in poll['votes'].items() if votes == max_votes]
    return ', '.join(most_popular_options)

# Reaction added to a message
@client.event
async def on_reaction_add(reaction, user):
    # Ignore reactions from the bot and reactions to messages that are not polls
    if user == client.user or reaction.message.channel.id not in polls:
        return

    # Get the poll corresponding to the message that was reacted to
    poll = polls[reaction.message.channel.id]

    # Get the option that was voted for
    option_index = int(reaction.emoji[0]) - 1
    if option_index < 0 or option_index >= len(poll['options']):
        return
    option = poll['options'][option_index]

    # Update the poll votes
    poll['votes'][option] += 1

    # Update the poll message with the new vote counts
    await reaction.message.edit(content=create_poll_message(poll))

    # Check if the poll has closed
    total_votes = sum(poll['votes'].values())
    remaining_time = (poll['closing_time'] - (discord.utils.utcnow() - reaction.message.created_at).total_seconds() // 60)
    if remaining_time <= 0:
        await close_poll(reaction.message, poll)
        previous_polls.append(poll)  # Add the closed poll to the previous polls list
    else:
        # Update the poll message with the remaining time
        await reaction.message.edit(content=create_poll_message(poll) + f'This poll will close in {remaining_time} minutes.')
        # Schedule the poll to close when the remaining time is up
        await asyncio.sleep(remaining_time * 60)
        if reaction.message.channel.id in polls:
            await close_poll(reaction.message, poll)
            previous_polls.append(poll)  # Add the closed poll to the previous polls list

# Display previous polls
async def display_polls(channel, start_index):
    end_index = start_index + 5
    if start_index >= len(previous_polls):
        await channel.send('No more polls to display.')
        return

    poll_chunk = previous_polls[start_index:end_index]
    for poll in poll_chunk:
        results_message = create_results_message(poll)
        most_popular_option = get_most_popular_option(poll)
        results_message += f"\n\nThe most popular option was: {most_popular_option}"
        await channel.send(results_message)

    if end_index >= len(previous_polls):
        await channel.send('No more polls to display.')
    else:
        await channel.send('Use `!polls next` to view the next 5 polls.')

# Run the bot
client.run('REMOVED-SECRET-FOR-SECURITY-PURPOSES')
