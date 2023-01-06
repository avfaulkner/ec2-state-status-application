# AWS EC2 Portal

The purpose of this portal is provide a principle location in which users can gain insight into a particular set of AWS EC2 instances.
Users will have access to the state status of the machines and more. 
The code relies on the machines existing within a database and also being tagged, as the tag will be used to provide users with additional state status information, such as the day/time of the state change.
The portal is created using Flask.
The current plan is to host and serve this portal using Fargate and Cloudfront in AWS.
