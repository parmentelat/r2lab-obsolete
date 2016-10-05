# These helpers target the MAC that is sitting in the R2lab chamber
# and has a USB connection to a commercial phone (nexus 6 as of now)

source $(dirname "$BASH_SOURCE")/r2labutils.sh

type -p adb >& /dev/null || alias adb="$HOME/nexustools/adb"

create-doc-category phone "tools for managing R2lab phone from macphone"
augment-help-with phone

doc-phone phone-on "turn off airplane mode"
function phone-on() {
    echo "Turning ON phone - i.e. turning off airplane mode"
    adb shell "settings put global airplane_mode_on 0; am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false"
}

doc-phone phone-off "turn off airplane mode"
function phone-off() {
    echo "Turning OFF phone - i.e. turning on airplane mode"
    adb shell "settings put global airplane_mode_on 1; am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true"
}

doc-phone phone-status "shows wheter airplane mode is on or off"
function phone-status() {
    airplane_mode_on=$(adb shell "settings get global airplane_mode_on")
    airplane_mode_on=$(echo $airplane_mode_on)
    case $airplane_mode_on in
	0*) echo phone is turned ON ;;
	1*) echo phone is turned OFF ;;
	*) echo "??? : got X${airplane_mode_on}X" ;;
    esac
}

doc-phone phone-reboot "reboot phone with abd reboot"
function phone-reboot() {
    echo "REBOOTING phone ..."
    #    adb shell am broadcast -a android.intent.action.BOOT_COMPLETED
    adb reboot
}

doc-phone refresh "retrieve latest git repo, and source it in this shell"
function refresh() {
    cd ~/r2lab
    git pull
    source ~/.bash_profile
}

# to set LTE only - except that sqlite3 is not known
#adb shell sqlite3 /data/data/com.android.providers.settings/databases/settings.db "update global SET value=11 WHERE name='preferred_network_mode'"
#adb shell sqlite3 /data/data/com.android.providers.settings/databases/settings.db "select value FROM secure WHERE name='preferred_network_mode'"

########################################
define-main "$0" "$BASH_SOURCE" 
main "$@"
