const inputs = document.querySelectorAll(".input-field");
const toggle_btn = document.querySelectorAll(".toggle");
const main = document.querySelector("main");
const bullets = document.querySelectorAll(".bullets span");
const images = document.querySelectorAll(".image");

inputs.forEach((inp) => {
    inp.addEventListener("focus", () => {
        inp.classList.add("active");
    });
    inp.addEventListener("blur", () => {
        if (inp.value != "") return;
        inp.classList.remove("active");
    });
});
toggle_btn.forEach((btn) => {
    btn.addEventListener("click", () => {
        main.classList.toggle("sign-up-mode");
    });
});

function LoginUserForm() {
    const username = document.getElementById('id_Username').value;
    const password = document.getElementById('id_Password').value;

    const credientials = {
        username: username,
        password: password
    }

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(credientials)
    }).then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/dashboard'
                alert('Login Sucessful')
            } else {
                alert('Login failed. Check your Credentials.')
            }
        }).catch(error => {
            console.error('Error:', error);
        });
}      

const CreateAccountLink = document.getElementById("CreateAccountLink");
CreateAccountLink.addEventListener("click", (event) => {
    event.preventDefault();
    window.location.href = CreateAccountLink.getAttribute('href');
    alert("Redirect to create account page");
});

const createAccountButton = document.getElementById('CreateAccountButton');
createAccountButton.addEventListener("click", () => {
    const username = document.getElementById("id_Username").value;
    const password = document.getElementById("id_Password").value;
    const email = document.getElementById("id_Email").value;
    // Add your login validation logic here
    if (username === "your_username" && password === "your_password" && email === "your email") {
        // Login successful
        alert("Account created successful!");
        // Redirect to a new page or perform other actions
    } else {
        alert("Please check your credentials.");
    }
});

const LoginLink = document.getElementById("LoginLink");
LoginLink.addEventListener("click", (event) => {
    event.preventDefault();
    window.location.href = LoginLink.getAttribute('href');
    alert("Redirect to Login page");
});

function moveSlider() {
    let index = this.dataset.value;

    let currentImage = document.querySelector(`.img-${index}`);
    images.forEach((img) => img.classList.remove("show"));
    currentImage.classList.add("show");

    const textSlider = document.querySelector(".text-group");
    textSlider.style.transform = `translateY(${-(index - 1) * 2.2}rem)`;

    bullets.forEach((bull) => bull.classList.remove("active"));
    this.classList.add("active");
}

bullets.forEach((bullet) => {
    bullet.addEventListener("click", moveSlider);
});
