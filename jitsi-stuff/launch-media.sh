#!/usr/bin/env bash
set -e

VIDEO="/mnt/virt-share/dbd_debate.mp4"
AUDIO="$VIDEO"
JITSI_URL="https://jitsi.local/testroom"
BOT_PROFILE="/tmp/firefox-bot-profile" # firefox bot profile

# Load Virtual Devices
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="BotCam" exclusive_caps=1
pactl load-module module-null-sink sink_name=BotSink

# Feed video
ffmpeg -re -stream_loop -1 -i "$VIDEO" -vcodec rawvideo -pix_fmt yuv420p -f v4l2 /dev/video10 >/dev/null 2>&1 &
# ffmpeg -re -stream_loop -1 -i "$VIDEO" -pix_fmt yuv420p -f v4l2 /dev/video10 >/dev/null 2>&1 &
VID_PID=$!

# Feed audio
ffmpeg -re -stream_loop -1 -i "$AUDIO" -f pulse -device BotSink >/dev/null 2>&1 &
AUD_PID=$!

# Start Chromium in fake X session
DISPLAY=:99 firefox -CreateProfile "botprofile /tmp/firefox-bot-profile"

#if [ ! -d "$BOT_PROFILE" ]; then
#    firefox --headless -CreateProfile "botprofile $BOT_PROFILE"
    # Start and close Firefox once to initialize the profile
#    firefox --no-remote --profile "$BOT_PROFILE" --headless about:blank &
#    sleep 5
#    pkill firefox
#fi


Xvfb :99 -screen 0 1280x720x16 &
XVFB_PID=$!
export DISPLAY=:99
sleep 5

#xvfb-run -s "-screen 0 1280x720x16" 
#chromium-browser
#ungoogled-chromium "$JITSI_URL" \
#    --no-sandbox \
#    --use-fake-device-for-media-stream \
#    --use-file-for-fake-video-capture=/dev/video10 \
#    --use-fake-ui-for-media-stream \
#    --autoplay-policy=no-user-gesture-required \
#    --start-fullscreen \
#    --disable-gpu \
#    --disable-software-rasterizer \
#    --disable-infobars &
#BROWSER_PID=$!

# Launch Firefox
firefox \
    --no-remote \
    --profile "$BOT_PROFILE" \
    --kiosk "$JITSI_URL" &
BROWSER_PID=$!

wait $BROWSER_PID

kill $VID_PID $AUD_PID $XVFB_PID
