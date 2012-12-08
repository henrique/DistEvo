#!/bin/sh

DISPATCH_NAME="fp_dispatch.py"
VM_RUNDIR="/var/run/lsci2012"
VM_SCRIPT_PATH="$VM_RUNDIR/$DISPATCH_NAME"

cat > script.txt << EOF
#!/bin/sh

mkdir $VM_RUNDIR
# Yo dawg, I heard you like cat, so I put a cat in your cat so you can cat while
# you cat
cat >> $VM_SCRIPT_PATH << EOF
EOF

cat ../vm/$DISPATCH_NAME >> script.txt
echo "EOF" >> script.txt
echo "chmod 755 $VM_SCRIPT_PATH" >> script.txt

../scripts/write-mime-multipart --output=lsci-fp-userdata \
	upstart-job.conf:text/upstart-job \
	script.txt:text/cloud-boothook

rm script.txt
