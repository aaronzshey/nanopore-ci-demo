# clone_validation_scheduler.sh
# requires one argument - today's Run ID
# This script will get all the barcodes
# Give it today's run ID

# by Aaron Shey, March 21 2025


export WDIR=/global/home/groups/fc_fpsdnaseq

if [ -z "$1" ]; then
  echo "Error: No argument provided. Please specify a run ID."
  exit 1
fi

echo "Using run ID ${1}\n"

for barcode_directory in $(find ${WDIR}/${1}/clone-validation/plate1 -maxdepth 1 -mindepth 1 -type d | sort); do
  sbatch ${WDIR}/src/clone_validation.sh ${1} ${barcode_directory##*/}
  echo "sbatch ${WDIR}/src/clone_validation.sh ${1} ${barcode_directory##*/}"
done

