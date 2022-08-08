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
        $('#logged-out').hide();
        var name = user.displayName;

        /* If the provider gives a display name, use the name for the
        personal welcome message. Otherwise, use the user's email. */
        var welcomeName = name ? name : user.email;

        user.getIdToken().then(function(idToken) {
          userIdToken = idToken;
        

          $('#user').text(welcomeName);
          $('#logged-in').show();

        });

      } else {
        $('#logged-in').hide();
        $('#logged-out').show();

      }
    });
    // [END gae_python_state_change]

  }

 
  var signOutBtn =$('#sign-out');
  signOutBtn.click(function(event) {
    event.preventDefault();

    firebase.auth().signOut().then(function() {
      console.log("Sign out successful");
      document.location.replace("/");
    }, function(error) {
      console.log(error);
    });
  });

  configureFirebaseLogin();
});