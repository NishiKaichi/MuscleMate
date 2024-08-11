// upload_image.js

document.addEventListener("DOMContentLoaded", function () {
  const profileImageInput = document.getElementById("profile_image");

  if (profileImageInput) {
    profileImageInput.addEventListener("change", function () {
      document.getElementById("profile-image-form").submit();
    });
  }
});
