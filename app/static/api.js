catchError = (response) => {
    if (response.response === "OK") {
        return response.payload
    } else if (response.response === "Fail") {
        throw new Error(response.error_message)
    }
}

apiCall = (url, method, payload) => {
    options = { method };
    if (method == "POST" && payload) {
        options.body = JSON.stringify(payload);
        options.headers = {
            "Accept": "*/*",
            "Content-Type": "application/json"
        }
    }
    return fetch(url, options)
        .then((response) => {
            return response.json();
        }).then(response => {
            return catchError(response);
        }).catch(exception => console.error(exception));
}

apiGetAllTags = () => {
    return apiCall('/api/tags')
}

apiGetTagsOfImage = (image_id) => {
    return apiCall(`/api/image/${image_id}/tag`)

}

apiApplyTagToImage = (image_id, tag_name) => {
    return apiCall(`/api/image/${image_id}/tag/${tag_name}`, "POST")

}

apiSetImageFocalPoint = (image_id, focus_x, focus_y) => {
    return apiCall(`/api/image/${image_id}/focus?x=${focus_x}&y=${focus_y}`, "POST")

}

apiRemoveTagFromImage = (image_id, tag_name) => {
    return apiCall(`/api/image/${image_id}/tag/${tag_name}`, "DELETE")

}

apiGetRandomImage = () => {
    return apiCall(`/api/image/random`)
}

apiGetMessageById = (message_id) => {
    return apiCall(`/api/message/${message_id}`)
}

apiGetAllMessages = () => {
    return apiCall(`/api/message`)
}

apiGetRandomMessage = () => {
    return apiCall(`/api/message/random`)
}

apiCreateNewMessage = (message) => {
    return apiCall(`/api/message`, "POST", { message })
}

apiGetImageById = (image_id) => {
    return apiCall(`/api/image/${image_id}`)

}

apiGetImageTagMatch = (taglist) => {
    return apiCall(`/api/image?tags=${taglist.join(',')}`)

}

apiGetSession = (session_id) => {
    return apiCall(`/api/session/${session_id}`)
}

apiGetAllSessions = () => {
    return apiCall(`/api/session`)
}

apiCreateSession = (image_id, message_id) => {
    return apiCall(`/api/session?image=${image_id}&message=${message_id}`, "POST")

}