#!/bin/bash
#
# Adapted from the Mineos demo script  RUN_MINEOS.sh
# Usage: RunMantles.sh model_name
# Available model names for the practical are pyrolite & chondrite.

mineosloc="./mineos-1.0.2/"

if test "$#" != 1; then
echo " Usage: RunMantles.sh model_name"
exit
fi

model=$1

if [  ! -f mineos_${model}.txt ];
then
    echo Model file  mineos_${model}.txt does not exist. Maybe try using prem_noocean, pyrolite or chondrite as the model names or check if step2 worked properly.
    exit
fi

#Remove the files this routine will make
for lett in R S T
do
    rm e${model}_${lett} ${model}_${lett} ${model}_test_${lett}.eigen ${model}_test_${lett}.eigen.dat/* Eigen_${lett}_${model}_ASC/*
    rmdir ${model}_test_${lett}.eigen.dat Eigen_${lett}_${model}_ASC
done

#=========================================================
# A. run minos_bran program for spheroidal, toroidal and  radial modes,
# where,  0<=n<=40, 0<=l<= to , 0<f<0.01 Hz,

echo "Step 1:  minos_bran runs for S modes"
${mineosloc}/minos_bran << EOF
mineos_${model}.txt
${model}_S
e${model}_S
1.0e-10 10
3
0 800 0.0 10.0 0 40
EOF

echo "Step 2:  minos_bran runs for R modes"
${mineosloc}/minos_bran << EOF
mineos_${model}.txt
${model}_R
e${model}_R
1.0e-10 10
1
0 0 0.0 10.0 0 40
EOF

echo "Step 3: minos_bran runs for T modes"
${mineosloc}/minos_bran << EOF
mineos_${model}.txt
${model}_T
e${model}_T
1.0e-10 10
2
2 800 0.0 10.0 0 40
EOF

#============================================================
# B. Convert minos_bran results to .eigen relations

echo "Step 4: eigen for S"
${mineosloc}/eigcon << EOF
3
mineos_${model}.txt
6371
${model}_S
e${model}_S
${model}_test_S
EOF
echo "Step 5: eigen for R"
${mineosloc}/eigcon <<EOF
1
mineos_${model}.txt
6371
${model}_R
e${model}_R
${model}_test_R
EOF
echo "Step 6: eigen for T"
${mineosloc}/eigcon << EOF
2
mineos_${model}.txt
6371
${model}_T
e${model}_T
${model}_test_T
EOF

# C. Convert binary eigenfunctions to ascii (not used in practical)
echo "Step 7: ascii eignefunctions"

#find actual range of n and l present
# removed dependence on gmt gmtinfo function here 
rmodes=`awk '{if ($2 ~/^s$/) print $1, $3}'  ${model}_R | awk 'NR==1{for(i=1;i<=NF;i++)min[i]=max[i]=$i;}
{for(i=1;i<=NF;i++){if($i<min[i]){min[i]=$i}else if($i>max[i])max[i]=$i;}}
END{printf"%d %d %d %d", min[1], max[1], min[2], max[2]}'`
smodes=`awk '{if ($2 ~/^s$/) print $1, $3}'  ${model}_S | awk 'NR==1{for(i=1;i<=NF;i++)min[i]=max[i]=$i;}
{for(i=1;i<=NF;i++){if($i<min[i]){min[i]=$i}else if($i>max[i])max[i]=$i;}}
END{printf"%d %d %d %d", min[1], max[1], min[2], max[2]}'`
tmodes=`awk '{if ($2 ~/^t$/) print $1, $3}'  ${model}_T | awk 'NR==1{for(i=1;i<=NF;i++)min[i]=max[i]=$i;}
{for(i=1;i<=NF;i++){if($i<min[i]){min[i]=$i}else if($i>max[i])max[i]=$i;}}
END{printf"%d %d %d %d", min[1], max[1], min[2], max[2]}'`
 
#Get the eigenfunctions fromt he binary files
#eigen2asc [-n] nmin nmax lmin lmax db_name out_dir
#

#radial
${mineosloc}/eigen2asc $rmodes ${model}_test_R Eigen_R_${model}_ASC
#sph
${mineosloc}/eigen2asc $smodes ${model}_test_S Eigen_S_${model}_ASC
#tor
${mineosloc}/eigen2asc $tmodes ${model}_test_T Eigen_T_${model}_ASC


#play with the output to make some easy to plot files

for lett in R S T
do
    #find the start of the results
    linesabv=`grep -n integration ${model}_R  | awk -F":" '{print $1+4}'`
    awk '{if (NR > '$linesabv') print $1, $2, $3, $5, $8}' ${model}_${lett} > ${model}_${lett}.out

    # a dispersion plot can be made using columns 3 and 4 of this file, a freq-q plot from 4&5.
    # these data can also be compared with REM output which will be formatted in the same way.
    
done
