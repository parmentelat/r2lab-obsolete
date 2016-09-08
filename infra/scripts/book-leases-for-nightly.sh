SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin

#WE ARE CALLING THIS SCRIPT ONCE A YEAR, at 01/01/YYYY 00:00 FROM FARADAYS CRONTAB

# Book each SUNDAYs and WEDNESDAYs in the whole current year (default when not date peiord is given)
python3 /root/r2lab/nightly/book-nightly.py -d sun,wed > /var/log/book-nightly.log 2>&1;

# EXAMPLES

# An example considering an specific date period and SUNDAYs and WEDNESDAYs
# If no weekday is given it will book every day
#python3 /root/r2lab/nightly/book-nightly.py -p 2016-9-8 2016-9-18 -d sun,wed > /var/log/book-nightly.log 2>&1;

# An example to book every day for the whole current year
#python3 /root/r2lab/nightly/book-nightly.py > /var/log/book-nightly.log 2>&1;
