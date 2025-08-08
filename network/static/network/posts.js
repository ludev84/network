document.querySelectorAll(".post>button").forEach(function(button) {
    button.onclick = function() {
        const content = document.querySelector(`#post-${button.id}-content`);

        if (button.dataset.type === "edit") {
            fetch(`post/${button.id}`)
            .then(response => response.json())
            .then(post => {
                content.innerHTML = '';
                textarea = document.createElement('textarea');
                textarea.classList.add('form-control');
                textarea.rows = '5';
                textarea.value = post.content;
                content.append(textarea);

                button.innerHTML = 'Save';
                button.classList.toggle('btn-success')
                button.dataset.type = "save"
                button.blur();
            })
        } else if (button.dataset.type === "save") {
            const new_content = content.querySelector("textarea").value
            fetch(`post/${button.id}`, {
                method: "PUT",
                body: JSON.stringify({
                    content: new_content,
                }),
            })
            .then(response => response.json())
            .then(result => {
                content.innerHTML = `<p>${new_content}</p>`;

                button.innerHTML = 'Edit';
                button.classList.toggle('btn-success')
                button.dataset.type = "edit"
                button.blur();
            })
        }
        
    }

})