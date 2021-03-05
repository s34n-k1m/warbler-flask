"use strict";

const $likeBtns = $(".like-button");
const BASE_URL = "http://127.0.0.1:5000";

/* Function makes a post request to /messages/{id}/like 
-adds like or deletes like from likes table */

async function addOrRemoveLike(id) {
  await axios({
    url: `${BASE_URL}/messages/${id}/like`,
    method: "POST"
  });
}

/* Handles clicking on a like button. */

async function handleBtnClick(evt) {
  console.log("CLICKED");
  let $likeIcon = $(evt.target);
  let $btn = $likeIcon.closest('button');
  let id = $btn.attr('data-id');

  await addOrRemoveLike(id);
  
  $likeIcon.toggleClass('liked-message unliked-message');
  $likeIcon.toggleClass('fas far');
}

/* Add event listener on like buttons */

function start() {
  console.log('HI THERE :>> ');
  for (let btn of $likeBtns) {
    let $btn = $(btn);
    $btn.on('click', handleBtnClick);
  }
}

start();