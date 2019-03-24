# python_flask_rest_app
RESTful application using python and flask for Cloud computing coursework.

# Introduction to App - 'All in one Dashboard'
This is a 'Task management' application that allows users to view,delete,assign tasks and sub-tasks. The following implementations are made as per mini-project specification

1. REST based application Interface (The application has more than 15 APIs performing GET and POST actions with HATEOAS implementation communicating with Cassandra Database)
2. Interaction with external REST services. (The application uses Twitter API to get top-10 tweets on a topic of user's choice)
3. Use of on an external Cloud database for persisting information. (The application uses cassandra deployed on gcloud cluster for storing persistent information for the application)
4. Support for cloud scalability, deployment in a container environment. (The steps for deploying the application can be found in later sections of this README file. Also a demonstration of deployment and cloud scalability will be presented to the course lecturer as instructed)
5. Cloud security awareness. (External API key, Password of users and other confidential information are abstracted by including them in config.py file or the database)

The above points are to be considered for 6/10 points and the below add-ons are implemented for 6 more points

1. Demonstration of load balancing and scaling of the application (e.g. kubernetes based load balancing, as well as Cassandra ring scaling)
    - *Testing load balancing* - The application provides many REST APIs starting with the route /rest/. All the responses have HATEOAS       implementation for navigation using APIs alone without the support of UI (However a basic HTML UI is also designed and is in              place). In those responses a field for *Host-IP* is included purposely to show the effect of load-balancing. 
       It can be seen that the same API's response will be having different  *Host-IP* values for everytime its called.
    - *Testing Cassandra ring scaling* - This will be demonstrated and the effect will be discussed in one of the lab sessions. The             scaling command is:
        **kubectl scale rc cassandra --replicas=n**
        *Where 'n' is the number of cassandra replicas*
    
2. Implemented cloud security measures.
    - The application is served over "HTTPS"
    - Hash based authentication - The user's passwords are hashed using sha256 and stored in the Database, instead of storing plaintext           password
    - Implementing user accounts and access management - The application has  types of users - admin, manager, user. The users are given         privileges based on their roles. The contents they can view or the actions they can perform are driven by their roles
    - Securing the database with role-based policies - Unauthorized users or users with insufficient privileges can't access content or           delete any records in the database
    
3. Any of the app components have a non-trivial purpose.

    - Request followup orchestration using HATEOAS - All the REST API responses from the application have HATEOAS implemented to present       to the user with urls for other REST APIs that might interest the user for navigation through API responses or Request followup         orchestration.
    
    - Complex database implementation including data schema design, or substantial write operations - The application uses 4 tables           (tasks,sub_tasks,users,login) and their relationship is as follows
                  
      
    
    
    
    
    
    
