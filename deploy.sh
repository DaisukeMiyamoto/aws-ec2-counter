#!/bin/bash -xe
PRODUCT_NAME="aws-ec2-counter"
BUCKET_NAME=midaisuk-public-templates
TEMPLATE_NAME=${PRODUCT_NAME}.yaml
BUILD_TEMPLATE_NAME=${PRODUCT_NAME}-build.yaml
INCLUDE_LAMBDA=src/ec2-counter-lambda.py
LAMBDA_SPACE="                    "
DEFAULT_STACK_NAME="EC2Counter"
TEMPLATE_URL="https://${BUCKET_NAME}.s3.amazonaws.com/${PRODUCT_NAME}"/${BUILD_TEMPLATE_NAME}

echo "" > $BUILD_TEMPLATE_NAME

cat $TEMPLATE_NAME | while IFS= read line
do
    if [ "$line" = "##INCLUDE_LAMBDA##" ]; then
        sed "s/^/${LAMBDA_SPACE}/" $INCLUDE_LAMBDA >> $BUILD_TEMPLATE_NAME
    else
        echo -e "$line" >> $BUILD_TEMPLATE_NAME
    fi
done

aws s3 cp ${BUILD_TEMPLATE_NAME} s3://${BUCKET_NAME}/${PRODUCT_NAME}/ --acl public-read

echo "Access this URL for deploy"
echo "https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=${DEFAULT_STACK_NAME}&templateURL=${TEMPLATE_URL}"