#!/bin/bash
now="$(date +'%m/%d/%Y')"
expired=$(date --date="${now} -4 day" +%m/%d/%Y)
pass_expired=$(date --date="${now} -2 day" +%m/%d/%Y)

output=`psql -U gnowak -d pagefund -c "update invitations_generalinvitation set expired = 't' where date_created < '$expired';"`
if [[ $output == *"UPDATE"* ]]; then
    echo "$now; set general_invitation expirations; SUCCESS; output: $output" >> scripts/log/expire.log
fi

output=`psql -U gnowak -d pagefund -c "update invitations_managerinvitation set expired = 't' where date_created < '$expired';"`
if [[ $output == *"UPDATE"* ]]; then
    echo "$now; set manager_invitation expirations; SUCCESS; output: $output" >> scripts/log/expire.log
fi

output=`psql -U gnowak -d pagefund -c "update invitations_forgotpasswordrequest set expired = 't' where date_created < '$pass_expired';"`
if [[ $output == *"UPDATE"* ]]; then
    echo "$now; set forgot_password_request expirations; SUCCESS; output: $output" >> scripts/log/expire.log
fi
