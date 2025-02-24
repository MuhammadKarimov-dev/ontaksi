document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript yuklandi!");

    // Tahrirlash tugmachasi uchun hodisa qo'shish
    let editButtons = document.querySelectorAll(".btn-primary");
    editButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            alert("Tahrirlash sahifasiga o'tmoqdasiz!");
            window.location.href = this.href;
        });
    });

    // O‘chirish tugmachasi uchun tasdiqlash
    let deleteButtons = document.querySelectorAll(".btn-danger");
    deleteButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            let confirmDelete = confirm("Ростдан ҳам бу эълонни ўчирмоқчимисиз?");
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });

    // Start va Stop tugmalari uchun interaktiv hodisalar
    let actionButtons = document.querySelectorAll(".btn-warning, .btn-success");
    actionButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            alert("Эълон ҳолати ўзгармоқда...");
            window.location.href = this.href;
        });
    });
});