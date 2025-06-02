Dropzone.autoDiscover = false;

function init() {
    let dz = new Dropzone("#dropzone", {
        url: "/classify_image",  // ✅ FIXED: Correct endpoint for POST
        maxFiles: 1,
        addRemoveLinks: true,
        dictDefaultMessage: "Upload an image of a sportsperson",
        autoProcessQueue: false,
        acceptedFiles: "image/*",
        init: function () {
            let submitBtn = document.querySelector("#submitBtn");
            let myDropzone = this;

            submitBtn.addEventListener("click", function () {
                if (myDropzone.getAcceptedFiles().length === 0) {
                    alert("Please upload an image first!");
                    return;
                }
                myDropzone.processQueue();
            });
        }
    });

    dz.on("addedfile", function () {
        if (dz.files[1] != null) {
            dz.removeFile(dz.files[0]);
        }
    });

    dz.on("sending", function (file, xhr, formData) {
        // Optional: can append extra form data here
    });

    dz.on("success", function (file, response) {
        let data = response;

        if (!data || data.length == 0) {
            $("#resultHolder").hide();
            $("#divClassTable").hide();
            $("#error").show();
            return;
        }

        let players = ["sachin_tendulkar", "maria_sharapova", "mithali_raj", "ms_dhoni", "virat_kohli"];


        let match = null;
        let bestScore = -1;
        for (let i = 0; i < data.length; ++i) {
            let maxScoreForThisClass = Math.max(...data[i].class_probability);
            if (maxScoreForThisClass > bestScore) {
                match = data[i];
                bestScore = maxScoreForThisClass;
            }
        }

        if (match) {
            $("#error").hide();
            $("#resultHolder").show();
            $("#divClassTable").show();
            $("#resultHolder").html($(`[data-player="${match.class}"`).html());
            let classDictionary = match.class_dictionary;
            for (let personName in classDictionary) {
                let index = classDictionary[personName];
                let proabilityScore = match.class_probability[index];
                let elementName = "#score_" + personName;
                $(elementName).html(proabilityScore.toFixed(2));
            }
        }
    });

    dz.on("error", function (file, errorMessage) {
        console.error("Upload failed:", errorMessage);
        $("#error").show().text("Upload failed. Please try a different image.");
    });
}

$(document).ready(function () {
    console.log("ready!");
    $("#error").hide();
    $("#resultHolder").hide();
    $("#divClassTable").hide();

    init();
});
