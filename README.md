# View Assist Companion - BETA

This is an Android application and Home Assistant integration to compliment the amazing [View Assist project by @dinki](https://github.com/dinki/View-Assist). It has been built from the ground up to simplify the setup of devices when using View Assist and provide a lower barrier to entry to get up and running.

## How is this different from existing solutions?

Other solutions are a combination of applications for voice and display and often have quite an involved setup. VACA is a 1-stop shop of voice and browser support providing a simplified setup with just a single Android application install. Built specifically for View Assist also means that it provides the features and capabilities needed to support this project, without having to piece other solutions together.

## Will it work for me?

It has been tested on the following devices:

- Lenovo ThinkSmart View
- Lenovo Smart Display 10"
- Lenovo Smart Clock 2
- Samsung S24
- Samsung Tab 6

If you are using a different device and have issues, please log an issue in the repository and we will do our best to solve it with you.

## So what does it do?

The integration and Android application together have the following features:

- Supports mdns/zeroconf for easy setup
- Uses the Wyoming protocol to provide an experience similar to setting up a HA Voice Preview Edition (except with a display!)
- Provides a web browser with auto loading of the HA dashboard upon connection from HA
- On device wakeword support to reduce network traffic of streaming wakeword solutions and remove the need to install openwakeword or similar.
  - Choose from 6 wakewords
  - Choose from 4 different wakeword detection sounds (plus a No sound option)
- Media player to support streaming audio (tested with Radio browser and Music Assistant)
- Microphone gain control and mute switch
- Screen controls to keep screen on (or let it sleep), set brightness and control auto brightness
- Pull down to refresh screen function
- Volume controls for voice responses, music and volume ducking (lowering music when listening for a command)
- Last command (STT) and response (TTS) sensors
- Sensors to show ambient light levels and device orientation (where available)
- Start on boot
- Securtity to prevent intrusion once paired to a HA server
- In app updates - v0.4.0 onwards

## Installation

There are 2 components to this solution, a HA custom integration and an Android application. Install the custom integration first and then install the app on your devices.

Devices should be auto discovered with mDns (zeroconf) and appear in the list of discovered devices in Devices & Services. If they do not, you can add them manually using the IP address displayed on your device on the 'waiting connection' screen and use port 10800.

If you have previously paired your device with a HA instance and deleted that setup or want to change the HA instance the device is connected to (or the IP of HA has changed), you will need to unpair your device. This can be done by long pressing on the logo on the waiting connection screen. You will see the paired device IP address revert to 'not paired'.

**NOTE**: You will need at least the 2025.7.0 version of the View Assist integration which has support for VACA to be able to select the microphone entity when setting up the device in View Assist

### Custom Integration

As is common with new custom integrations, it can take a little while to be fully available via HACs. However, you can add this as a custom respository by using the following link to then provide the normal HACs install and update experience.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=msp1974&repository=ViewAssist_Companion_App&category=Integration)

### Android Application

The app is not currently available in the Play store and will need to be downloaded from the release assets in this repository and installed on your device. [Latest release](https://github.com/msp1974/ViewAssist_Companion_App/releases/latest)

# Diagnostics Overlay (v0.3.4 and above)

We have added an experimental feature in v0.3.4 to provide an overlay on the screen, displaying microphone audio level and wake word prediction value to aide with voice issues - be it not hearing wake word, too many false positives, poor interpretation of commands or just pure geeky interest!

This feature can be enabled/disabled using the `On screen diagnostics` switch entity in the VACA integration device.

Please read the below to understand what this is showing you.

### Microphone audio level

This is the level of audio being processed by the wake word engine (while waiting for wake word) or being sent to the Speach To Text (STT) engine when the wake word has been detected.

You will notice on some devices that the audio level seems very low (in the 0.00x level) and on others much higher (in the 0.x level) when listening for the wake word. This is ok (it is a feature of the device hardware/OEM Android config) and the wake word detection engine will work just as well. **NOTE**: The gain setting makes no difference to this level.

Once the wake word is detected, VACA switches into STT mode to stream audio over the network to HA and you will see a significant jump in the audio level (in the 1.x to 5.x range). This is where the auto gain function has kicked in to boost the audio level (to try and be consistent no matter the device) and improve the command interpretation by your chosen STT engine. The mic gain setting is in effect here. You should expect this level to be in the high 2.x to 3.x range with gain at 0. Dropping to 1.x at -10 and increasing to 4-5.x at +10.

So, why not boost the audio level for wake word detection? Well, very good question. And the answer is, we tried that and it actually made it worse in real world testing, so we removed it.

### Wake word prediction

This is the wake word engine's level of confidence that the audio heard was the wake word when in wake word listening mode. In the settings, there is a wake word threshold setting, which directly relates to this prediciton number. Ie, once this prediction number is greater than the threshold level, it will class that as a wake word detection.

A setting of 6 on the threshold setting should be a good place to start to find the right balance for good detection without many false detections in noisier environments.

Some wake words are better at detecting/less sensitive to accents than others and you may need to adjust this threshold setting if you change the wake word you wish to use, and this diagnostic overlay should help you get that setting right for you.

# FAQs

### My device won't load the HA webpage / I get page not found error with the wrong address

In most cases, this will be in cases where your HA is setup with SSL or behind a proxy and you have not setup the local network url in HA to reflect the correct address. VACA uses this information if it is populated and (if not) uses the IP of the server that connected ot the device and its configured port (default: 8123). Please ensure the internal url is correctly set in Settings -> System -> Network of you HA instance.

An additional issue could be that you are using self signed certificates in your SSL config. You need at least v0.4.0 to be able to use self signed certificates and select accept/always accept on the warning message that appears when connecting.

---

### My device doesn't pick up the wake word or picks up too many false positives

Try adjusting the wake word threshold. It is default set to 6 but play around with it until it works the best. The lower the setting the more it will detect but becomes more suseptable to fale positives. The higher it is, the more likley background noise will stop it detecting. Also see diagnostics overlay section.

---

### I dont understand how to turn the screen off on my device

There is some variation here with how devices will turn on/off their screens.

- Lenovo TSV - use the keep screen on switch and set the screen timeout on your device low. When keep screen on if set to off, it will sleep on this screne timeout. Turin keep screen on back to on, will wake up the screen.
- Lenovo LSD - use the brightness slider and set to 0 to turn screen off
- Lenovo SC2 - set auto brightness to off and then set brightness to 0.
- Other devices - try any of the above solutions. In the main, the more modern the device the more likley the TSV solution is the right answer.

---

### Can I use a custom wake word

This is a future ambition but for now it is limited to those listed and built into the app

---

### Can I use a custom wake word sound

See above answer!

---
