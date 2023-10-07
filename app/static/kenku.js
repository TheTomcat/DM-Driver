catchError = (response) => {
    if (response.response === "OK") {
        return response.payload
    } else if (response.response === "Fail") {
        throw new Error(response.error_message)
    }
}

const baseKenkuURI = 'http://127.0.0.1:3333/v1/';

kenkuApiCall = (url, method, payload) => {
    options = { method };
    if (method == "POST" || method == "PUT" || payload) {
        options.body = JSON.stringify(payload);
        options.headers = {
            "Accept": "*/*",
            "Content-Type": "application/json"
        }
    }
    return fetch(`${baseKenkuURI}${url}`, options)
        .then((response) => {
            return response.json();
        }).catch(exception => console.error(exception));
}

kenkuGetSoundboard = () => {
    return kenkuApiCall(`soundboard`)
}

kenkuPlaySoundboard = (idstring) => {
    return kenkuApiCall(`soundboard/play`, "PUT", { id: idstring })
}

kenkuStopSoundboard = (idstring) => {
    return kenkuApiCall(`soundboard/stop`, "PUT", { id: idstring })
}

kenkuGetSoundboardState = () => {
    return kenkuApiCall(`soundboard/playback`)
}

kenkuGetPlaylist = () => {
    return kenkuApiCall(`playlist`)
}

kenkuPlayPlaylist = (idstring) => {
    return kenkuApiCall(`playlist/play`, "PUT", { id: idstring })
}

kenkuGetPlaylistState = () => {
    return kenkuApiCall(`playlist/playback`)
}

kenkuResumePlaylist = () => {
    return kenkuApiCall(`playlist/playback/play`, "PUT")
}

kenkuPausePlaylist = () => {
    return kenkuApiCall(`playlist/playback/pause`, "PUT")
}

kenkuPlaylistNextTrack = () => {
    return kenkuApiCall(`playlist/playback/next`, "POST")
}

kenkuPlaylistPreviousTrack = () => {
    return kenkuApiCall(`playlist/playback/previous`, "POST")
}

kenkuPlaylistMute = (mute) => {
    return kenkuApiCall(`playlist/playback/mute`, "PUT", { mute })
}

kenkuPlaylistSetVolume = (volume) => {
    return kenkuApiCall(`playlist/playback/volume`, "PUT", { volume })
}

kenkuPlaylistShuffle = (shuffle) => {
    return kenkuApiCall(`playlist/playback/shuffle`, "PUT", { shuffle })
}

kenkuPlaylistRepeat = (repeat) => {
    return kenkuApiCall(`playlist/playback/repeat`, "PUT", { repeat })
}

