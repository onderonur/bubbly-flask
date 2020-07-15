# Bubbly-Flask
This is a clone of my own project [bubbly](https://github.com/onderonur/bubbly), with a python (flask) API created w/ [flask-socketio](https://flask-socketio.readthedocs.io/en/latest/).
A dynamic chat application created w/ Socket.IO, React, TypeScript and Express, Node.js.  
Live demo with Node.js API deployed on Heroku is **[here](https://bubbly-chat.herokuapp.com/)**.  
**Note:** This project is not up-to-date with the Node.js version. This is rather an experimental project to practice Python.

<p align="center">
  <img src="/assets/home-page.png" alt="Bubbly Logo"/>
</p>

### Features
* Creating chat rooms for real-time chat
* Joining conversations by using themed rooms
* JWT based anonymous authentication
* Users can set their username and conversation bubble color
* Sending images/gifs
* Emoji picker
* "User is typing" notifications
* Dark theme
* Automatically linkifying urls, emails etc
* Invite/share buttons
* Sound notification when the window is not focused
* "Back to bottom" button to scroll down automatically

### Stack
* API Framework: [Flask](https://flask.palletsprojects.com/)
* Real-Time Engine: [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)
* Authentication: [JSON Web Token](https://jwt.io/)
* UI Components: [Material-UI](https://material-ui.com/)
* Styling: [styled-components](https://styled-components.com/)
* Forms: [Formik](https://jaredpalmer.com/formik)
* Form Validations: [Yup](https://github.com/jquense/yup)
* Illustrations: [unDraw](https://undraw.co/)
* Linting: [ESLint](https://eslint.org/)
* Code formatting: [Prettier](https://prettier.io/)

### Development
To run it in development mode:
##### API:
#### `cd api`
#### `python -m venv env`
#### `env/Scripts/Activate`
#### `pip install`
#### `python app.py`
##### Client:
#### `cd client`
#### `npm install`
#### `npm start`
