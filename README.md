# B2-PLUTONIUM-REPORTER
Plutonium reporter is a tool for collecting data that can help narrow down issues with Plutonium launcher.

## How to download

Head to the [most recent release](https://github.com/B2ORG/B2-PLUTONIUM-REPORTER/releases/latest) and download `Plutonium Reporter.exe` file.

## Windows is telling me this program is potentially dangerous / is a virus

Python programs exported as an executable usually cause Windows to be suspitious, in order to deal with that I'd have to pay for a certificate, and it doesn't make sense for this project.

This program can be ran from source, in which case you will not get similar prompts, however it requires some tech savviness.

## How to use it

This program is meant to aid Plutonium support, it WILL NOT fix any issues on it's own. Once you've made contact with someone regarding your issue, and you've been asked to provide logs files/configs/crashdumps, that's where this tool comes to play.

> [!WARNING]
> When troubleshooting Plutonium issues, time is of the essence. The log files can override themselves over time. If you run into any problems, reach out to support immidiately, you can collect the report instantly and provide it to the support once you're asked about it.

1) Launch the program

You can launch the program from any place on your PC, except for when your Plutonium installation is not in default path:

```
C:\Users\<your username>\AppData\Local\Plutonium
```

If you do not know what this is about, it most likely does not apply to you. But in case you've placed Plutonium in another place on your pc, you need to put the reporter the main Plutonium directory, otherwise it won't be able to locate the relevant files.

> [!TIP]
> Plutonium installation IS NOT the same as your game files. It DOES NOT matter where the actual game is installed.

2) Select the crashdump file

Once launched, the program will display info about detected Plutonium path, if the patch is found successfully, it's time to select the relevant crashdump file. The files are numbered and each contains the version of Plutonium (eg. r5202), game (eg. t6zm) and date of the crash. If your issue is related to a crash and you see the file that matches that event, select it by typing the correct number and pressing ENTER. If you have another issue or the crashdump from your crash isn't on the list, just press ENTER.

3) Game selection

This is only a step if the crashdump file has not been selected. Simply choose which game the issue occured in by entering the correct number and pressing ENTER.

4) Finalize

The program will now collect all the necessary data. Once that's done, you'll see a message

```
Press ENTER to finish
```

At this point you can just press enter or close the program, the report file is now present in the same place as the reporter tool itself.

## Typical questions

- What kind of files does this program extract

It grabs log files from Plutonium, crashdumps (snapshots of memory from the moment of a crash), all your Plutonium configs, checksums of the files present in Plutonium directory, windows events related to Plutonium crashes, information about your PC hardware (like CPU, GPU etc) and Windows power settings.

- Is any information leaving my PC just by launching this program

No. The only output from this program is a report file generated at the end. You are free to examine the contents of the zip file before sending it to the person helping you with your problem. **IT DOES NOT** send anything over the network, should there ever be any kind of network integration in the future update, the user will always be asked for consent.

- Why do you need such an extensive dataset

It comes from helping many players with various issues, from obscure crashes during long zombies games, through performance issues all the way up to misbehaving scripts. All of this data we had to collect from players at one point or another.

- How can i upload the report file, it's too big for Discord message

If the report includes a crashdump, it can indeed get quite beefy. From our experience, players usually send us bigger reports using [Google Drive](https://drive.google.com/).

- How can i reach Plutonium support

The expected chain of events is someone who is helping you point you here in order to get and use the tool, but if for any reason it's the other way around, [Plutonium official Discord server](https://discord.gg/plutonium) is a good place to look for help.

- Why no user interface

To be frank, to save time. This tool works either way, and you don't need to do too much of interacting with it aside from telling it which crashdump/game to use.
