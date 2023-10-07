
function autocompleteTag(inputElement, tagList, onSubmit) {
    /*the autocomplete function takes three arguments,

    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    console.log(tagList);
    /*execute a function when someone writes in the text field:*/
    inputElement.addEventListener("input", function(e) {
        var autocompleteList, autocompleteItem, i, currentText = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!currentText) { return false;}
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        autocompleteList = document.createElement("DIV");
        autocompleteList.setAttribute("id", this.id + "autocomplete-list");
        autocompleteList.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(autocompleteList);
        /*for each item in the array...*/
        tagList.forEach((item) => {
            if (item.tag.toUpperCase().includes(currentText.toUpperCase())) {
                autocompleteItem = document.createElement("DIV");

                startPosition = item.tag.toUpperCase().indexOf(currentText.toUpperCase());
                prefix = item.tag.substr(0,startPosition);
                suffix = item.tag.substr(startPosition + currentText.length)
                
                autocompleteItem.innerHTML = `${prefix}<strong>${currentText}</strong>${suffix}`;
            
                //autocompleteItem.setAttribute('data-tag', item.tag)
                //autocompleteItem.setAttribute('data-tagid', item.id)
                autocompleteItem.dataset.tag = item.tag;
                autocompleteItem.dataset.tagid = item.id;

                autocompleteItem.addEventListener("click", function(e) {
                    inputElement.value = ""; //this.dataset.tag;
                    closeAllLists();
                    onSubmit({tag:e.target.dataset.tag, id:e.target.dataset.tagid});
            });
            autocompleteList.appendChild(autocompleteItem);
            }
        })

    });
    /*execute a function presses a key on the keyboard:*/
    inputElement.addEventListener("keydown", function(e) {
        var autocompleteList = document.getElementById(this.id + "autocomplete-list");
        if (autocompleteList) autocompleteList = autocompleteList.getElementsByTagName("div");
        if (e.keyCode == 40) {
            e.preventDefault();
          /*If the arrow DOWN key is pressed,
          increase the currentFocus variable:*/
          currentFocus++;
          /*and and make the current item more visible:*/
          this.value = autocompleteList?.[currentFocus].dataset.tag || "";
          addActive(autocompleteList);
        } else if (e.keyCode == 38) { //up
            e.preventDefault();
          /*If the arrow UP key is pressed,
          decrease the currentFocus variable:*/
          currentFocus--;
          /*and and make the current item more visible:*/
          this.value = autocompleteList?.[currentFocus].dataset.tag || "";
          addActive(autocompleteList);
        } else if (e.keyCode == 13) {
          /*If the ENTER key is pressed, prevent the form from being submitted,*/
          e.preventDefault();
          if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            if (autocompleteList) {
                autocompleteList[currentFocus].click();
            } 
          } else {
            if (autocompleteList && autocompleteList.length >= 1 && autocompleteList[0].dataset.tag === this.value) {
                //TODO: Probably gonna let the bugs in here
                id = autocompleteList[0].dataset.tagid;
                autocompleteList[0].click();
            } else {
                id = undefined;
                onSubmit({tag:this.value, id: id});
            }
            }
        }
    });
    function addActive(autocompleteList) {
      /*a function to classify an item as "active":*/
      if (!autocompleteList) return false;
      /*start by removing the "active" class on all items:*/
      removeActive(autocompleteList);
      if (currentFocus >= autocompleteList.length) currentFocus = 0;
      if (currentFocus < 0) currentFocus = (autocompleteList.length - 1);
      /*add class "autocomplete-active":*/
      autocompleteList[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(autocompleteList) {
        Array.from(autocompleteList).forEach(item => {
            item.classList.remove("autocomplete-active");
        })
      /*a function to remove the "active" class from all autocomplete items:*/
    }
    function closeAllLists(preserveElement) {
      /*close all autocomplete lists in the document,
      except the one passed as an argument:*/
      var x = document.getElementsByClassName("autocomplete-items");
      Array.from(x).forEach(element => {
        if (preserveElement != element && preserveElement != inputElement) {
            element.parentNode.removeChild(element);
          }
      })
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
  }