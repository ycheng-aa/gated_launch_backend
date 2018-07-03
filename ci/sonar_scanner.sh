#!/bin/bash
########执行sonar检查########
FLAG=$1
if [[ "$FLAG" = "y"  ]];then
    GERRIT_PROJECT=$2
	testReport=$3
	coverageReport=$4
	GERRIT_REFNAME=$5
	GERRIT_EVENT_ACCOUNT_NAME=$6
	
	temp=${GERRIT_PROJECT//\//_}
	
	if [[ "$GERRIT_REFNAME" = "n" ]];then
	    echo $GERRIT_REFNAME
	    echo $GERRIT_EVENT_ACCOUNT_NAME
	    coverage xml -i --omit=*/migrations/*,*/testcases/*
	    /var/wd/code_analysis/sonar-scanner-2.8/bin/sonar-scanner -Dsonar.projectKey=ffan.${temp}.${GERRIT_EVENT_ACCOUNT_NAME} -Dsonar.projectName=commits/${GERRIT_EVENT_ACCOUNT_NAME} -Dsonar.sources=. -Dsonar.language=py -Dsonar.projectVersion=1.0 -Dsonar.python.xunit.reportPath=$testReport -Dsonar.python.coverage.reportPath=$coverageReport
	else
	    coverage xml -i --omit=*/migrations/*,*/testcases/*
	    /var/wd/code_analysis/sonar-scanner-2.8/bin/sonar-scanner -Dsonar.projectKey=ffan.${temp} -Dsonar.projectName=commits/${GERRIT_PROJECT} -Dsonar.sources=. -Dsonar.language=py -Dsonar.projectVersion=1.0 -Dsonar.python.xunit.reportPath=$testReport -Dsonar.python.coverage.reportPath=$coverageReport
	fi	
    #######此半段else暂时未用########
else
    PROJECT_NAME=$2
	BRANCH=$3
	SOURCE=$4
	UT=$5
	testReport=$6

	curl -v -X POST -s -w%{http_code}  http://sonarapi.intra.sit.ffan.com/v1/sonar_start -d '{"projectName":"'$PROJECT_NAME'","sources":"'$SOURCE'","language":"py","isParent":"n","branch":"'$BRANCH'","gitType":"gerrit","UT":"'$UT'","testReport":"'$testReport'"}'
fi

sleep 5s

#######检查sonar结果#######
if [[ "$GERRIT_REFNAME" = "n" ]];then
    log=`curl -G -d "resource=ffan.${temp}.${GERRIT_EVENT_ACCOUNT_NAME}&metrics=alert_status,bugs,vulnerabilities" http://sonar.intra.ffan.com/api/resources`
else
    log=`curl -G -d "resource=ffan.${temp}&metrics=alert_status,bugs,vulnerabilities" http://sonar.intra.ffan.com/api/resources`
fi

bugs=`echo $log |awk -F "bugs" '{print $2}' |awk -F '"val":' '{print $2}' |awk -F "," '{print $1}'`
vulnerabilities=`echo $log |awk -F "vulnerabilities" '{print $2}' |awk -F '"val":' '{print $2}' |awk -F "," '{print $1}'`
if [[ "$bugs" = "0.0" ]];then
    if [[ "$vulnerabilities" = "0.0" ]];then
	    echo "INFO:Bugs and Vulnerabilities is 0, sonar successed!"
        exit 0
    else
	    echo "ERROE:Vulnerabilities is $vulnerabilities, results failed!"
        exit 1
    fi
else
    echo "ERROR:Bugs is $bugs, results failed!"
    exit 1
fi


