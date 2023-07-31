[Documentation](https://coral-sphynx-6db.notion.site/Conversational-AI-Google-DialogFlow-CX-d685704b40b94da688c7ba680e2d1baf?pvs=4)


### LLD : Low Level Design

- Setup Google Project for [DialogFlow-CX](https://cloud.google.com/dialogflow/cx/docs/quick) - for Conversational AI Agent and flows
- Setup [Cloud Meta APIs](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages) - To have a WhatsApp test number
- Clone the Git Repo
- Setup [AWS Account](https://aws.amazon.com/free/?trk=fb8718a7-d9f7-4e07-9fc5-b85de26b4178&sc_channel=ps&ef_id=CjwKCAjwt52mBhB5EiwA05YKo7emadU901YUKxZSe-py5Sg-Yl5XWkfCR569DjrLhwXVjaCNzGnXhhoCi4gQAvD_BwE:G:s&s_kwcid=AL!4422!3!531446682875!e!!g!!amazon%20free%20cloud%20server!11542865500!116152064367)(free Tier)
- [Setup Zappa](https://github.com/zappa/Zappa) - Inside your code terminal, For Serverless Deployment

> Now we are good to go! Deploy the Application and start testing.
> 

---

### Scalability

- Session Management :
    - Session management is required as GDF asks users to have a session ID and based on that the conversation flows.
    - For Session Management - Redis or other alternatives can be used
    - TODO :
        - Delete a session if expires
        - Maintain incomplete conversations active even if it crosses session timeout of 30 mins([refer link](https://cloud.google.com/dialogflow/cx/docs/concept/session))
        - Maintain session storage available to all the users through a single window - While using micro-service architecture as each time requests can go to any server in process of balancing the load
- Micro-Services Architecture:
    - We need to have a micro-service architecture for having high availability
    - We need consistency as well in regards to data(Session | User Conversation History)