![image](https://github.com/user-attachments/assets/cb6d3737-076e-4aa9-a895-bd0e3318cb64)



Why did I implement it this way:

I mainly stuck to the idea of the project supposed to be like Whatsapp.

So I tried to create a backend with some of whatsapps basic features:
You can send audios, images, create group chats, text other people seperately, create and delete accounts, login and log out from them and chose a simple database for django (postgresql).

Since this is the most used approach, I went into the API direction, to stay with whatsapp. Since whatsapp also (probably) works with a REST API approach, I created an API and used serializers for the main objects to keep the code simple.

The database models, the serializers, url paths and also the views are divided into four categories: Sessions, Uses, Chats and Messages. 

This way I don't get confused by the interconnection with the different layers.

Talking about different layers: I also tried to implement the classic Django idea of fat models, thin views. I tried to get most of the funcionality inside of the model and sometimes the serializers,
and use the views just to display that logic in a function specific way. 





WHat you were planning to do and didnt complete:

I wanted to add proper image storage (now its just stored in folders)
