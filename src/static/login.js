'use strict';
$(function(){
  // [START gae_python_firenotes_config]
  // Obtain the following from the "Add Firebase to your web app" dialogue
  // Initialize Firebase
  var config = {
    apiKey: "AIzaSyBfRjX4xdVNw1DmAnaN9HOsR5DlYsRM2o0",
    authDomain: "EvetinyIndustry.firebaseapp.com",
    projectId: "EvetinyIndustry",
    //databaseURL: "https://<DATABASE_NAME>.firebaseio.com",
    //storageBucket: "<BUCKET>.appspot.com",
    //messagingSenderId: "<MESSAGING_SENDER_ID>"

  };
  // [END gae_python_firenotes_config]

  // This is passed into the backend to authenticate the user.
  var userIdToken = null;
  
  // Firebase log-in
  function configureFirebaseLogin() {

    firebase.initializeApp(config);

    // [START gae_python_state_change]
    firebase.auth().onAuthStateChanged(function(user) {
      if (user) {

        user.getIdToken().then(function(idToken) {
        userIdToken = idToken;
        
          $('#logged-in').show();
         
          $.ajax('/login', {
            headers: {
              'Authorization': 'Bearer ' + userIdToken
            },
            method: 'POST',
            data: JSON.stringify({'displayName': user.displayName}),
            contentType : 'application/json'
          }).done(function(){
            window.location.replace('/home');
          });
        });

      } 
    });
    // [END gae_python_state_change]

  }

  // [START gae_python_firebase_login]
  // Firebase log-in widget
  function configureFirebaseLoginWidget() {
    var uiConfig = {
      'signInSuccessUrl': '/',
      'signInOptions': [
        // Leave the lines as is for the providers you want to offer your users.
        firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        firebase.auth.FacebookAuthProvider.PROVIDER_ID,
        firebase.auth.TwitterAuthProvider.PROVIDER_ID,
        firebase.auth.GithubAuthProvider.PROVIDER_ID,
        firebase.auth.EmailAuthProvider.PROVIDER_ID
      ],
      // Terms of service url
      'tosUrl': '<your-tos-url>',
    };
    firebase.auth().setPersistence(firebase.auth.Auth.Persistence.SESSION)
    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
  }
  // [END gae_python_firebase_login

  configureFirebaseLogin();
  configureFirebaseLoginWidget();
});