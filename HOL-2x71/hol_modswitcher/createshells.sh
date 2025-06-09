#!/bin/bash
# version 1.2 - 03 February 2023

# the highest number of modules in any lab SKU
modules=8

isempty=`find /hol/ModuleSwitcher/module-scripts -maxdepth 0 -empty -exec echo True \;`
if [ "${isempty}" = "True" ];then
	echo "Creating placeholder scripts for ModuleSwitcher..."
else
	echo "Delete existing module scripts before running."
	echo "Exit."
	exit
fi

while read s;do
	sku=${s:4:7}
	mod=0
	while [ $mod -lt ${modules} ];do
		mod=`expr $mod + 1`
		script="module-scripts/$sku-module-${mod}.sh"
		echo -e "#!/bin/bash\necho \"This is the $sku Module $mod script.\""  > $script
		chmod 774 $script
	done
done < skulist.txt

echo -e "\nDelete the placeholder scripts you don't need."
echo "Implement the fast-forward automation needed to skip to the selected module."
