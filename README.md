# ESTR4312_Porject
## Topic
personal album
## Features
1. Automatic add tags to images
2. User can add visual effect to their images while uploading. e.g. blurring, decoloring, blending, high dynamic range, picture mixing, etc.
3. Periodically send email digest of trending tags
4. Search image using tags
5. (Probably) Social network

## Architecture
![](design.png)

## Stack
* web server: Nginx
* app server: Flask
* message queue: rabbitMQ
* auto tagging: Imagga
* visual effect: OpenCV
* email digest: SendGrid
* database: MySQL
* Cache: Redis
* Social network: Stream

## Milestone
1. End of November: Feature 1, 3, 4
2. End of December: Feature 2, 5(probably)
