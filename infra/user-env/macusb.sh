# These helpers target the MAC that is sitting in the R2lab chamber
# and has a USB connection to a commercial phone (nexus 6 as of now)

function phone-on() {
    echo "Turning ON phone - i.e. turning off airplane mode"
    adb shell "settings put global airplane_mode_on 0; am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false"
}

function phone-off() {
    echo "Turning OFF phone - i.e. turning on airplane mode"
    adb shell "settings put global airplane_mode_on 1; am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true"
}

function phone-status() {
    airplane_mode_on=$(adb shell "settings get global airplane_mode_on")
    airplane_mode_on=$(echo $airplane_mode_on)
    case $airplane_mode_on in
	0*) echo phone is turned ON ;;
	1*) echo phone is turned OFF ;;
	*) echo "??? : got X${airplane_mode_on}X" ;;
    esac
}

function phone-reboot() {
    echo "REBOOTING phone ..."
    #    adb shell am broadcast -a android.intent.action.BOOT_COMPLETED
    adb reboot
}

function phone() {
    mode=$1; shift
    command=phone-$mode
    what=$(type -t $command) && $command || echo "Unknown mode $mode"
}
	
function refresh() {
    cd ~/r2lab
    git pull
    source ~/.bash_profile
}


# to set LTE only - except that sqlite3 is not known
#adb shell sqlite3 /data/data/com.android.providers.settings/databases/settings.db "update global SET value=11 WHERE name='preferred_network_mode'"
#adb shell sqlite3 /data/data/com.android.providers.settings/databases/settings.db "select value FROM secure WHERE name='preferred_network_mode'"
