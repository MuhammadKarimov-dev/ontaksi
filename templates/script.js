document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".start-btn").forEach(button => {
        button.addEventListener("click", function () {
            let announcementId = this.getAttribute("data-id");
            let btn = this;
            
            btn.innerText = "Ishlayapti...";
            btn.disabled = true;

            fetch(`/start-announcement/${announcementId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    btn.innerText = "To‘xtatish";
                    btn.classList.add("stop-btn");
                    btn.classList.remove("start-btn");
                } else {
                    btn.innerText = "Qayta urinib ko‘ring";
                    btn.disabled = false;
                }
            })
            .catch(error => {
                console.error("Xato:", error);
                btn.innerText = "Xatolik!";
                btn.disabled = false;
            });
        });
    });
});