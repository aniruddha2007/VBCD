//update total count
function updateTotalCount() {
    var totalCount = document.getElementById("index-table").rows.length - 1; // Subtract header row
    document.getElementById("totalCount").innerText = `名片總數:${totalCount}`;
}

//copy selected emails
function copySelectedEmails() {
    var table = document.getElementById("index-table");
    var rows = table.rows;
    var selectedEmails = [];

    // Iterate through rows and check if the checkbox is selected
    for (var i = 1; i < rows.length; i++) {
        var checkbox = rows[i].getElementsByTagName("input")[0];
        var emailCell = rows[i].getElementsByTagName("td")[7]; // Adjust index based on your table structure

        if (checkbox.checked) {
            selectedEmails.push(emailCell.innerText.trim());
        }
    }

    // Join selected emails into a string
    var emailsString = selectedEmails.join(", ");

    // Create a textarea element to copy the text
    var textarea = document.createElement("textarea");
    textarea.value = emailsString;
    document.body.appendChild(textarea);

    // Select the text inside the textarea
    textarea.select();
    textarea.setSelectionRange(0, 99999); // For mobile devices

    try {
        // Execute the copy command
        var successful = document.execCommand('copy');
        var message = successful ? 'successful' : 'unsuccessful';
        console.log('Copying text command was ' + message);
    } catch (err) {
        console.error('Unable to copy text to clipboard', err);
    }

    // Remove the textarea element
    document.body.removeChild(textarea);
}

//Download selected contacts
function downloadSelectedContacts() {
    var table = document.getElementById("index-table");
    var rows = table.rows;
    var selectedContacts = [];

    // Iterate through rows and check if the checkbox is selected
    for (var i = 1; i < rows.length; i++) {
        var checkbox = rows[i].getElementsByTagName("input")[0];

        if (checkbox.checked) {
            // Get the contact data from the corresponding row for 標籤, 名字, 姓氏, 公司, 部門, 職稱, 電子郵件地址, 電子郵件地址 2, 商務電話, 手機號碼, 商務傳真, 生日, 商務地址, 商務城市, 商務州, 商務郵遞區號, 商務國家, 網頁, 認識日期, 備註
            var contact = {
                tag: rows[i].cells[1].innerText,
                firstName: rows[i].cells[2].innerText,
                lastName: rows[i].cells[3].innerText,
                company: rows[i].cells[4].innerText,
                department: rows[i].cells[5].innerText,
                jobTitle: rows[i].cells[6].innerText,
                emailAddress: rows[i].cells[7].innerText,
                emailAddress2: rows[i].cells[8].innerText,
                businessPhone: rows[i].cells[9].innerText,
                mobilePhone: rows[i].cells[10].innerText,
                businessFax: rows[i].cells[11].innerText,
                birthday: rows[i].cells[12].innerText,
                businessAddress: rows[i].cells[13].innerText,
                businessCity: rows[i].cells[14].innerText,
                businessState: rows[i].cells[15].innerText,
                businessZip: rows[i].cells[16].innerText,
                businessCountry: rows[i].cells[17].innerText,
                webPage: rows[i].cells[18].innerText,
                meetDate: rows[i].cells[19].innerText,
                notes: rows[i].cells[20].innerText,
                // Add more properties as needed
            };

            selectedContacts.push(contact);
        }
    }

    // Convert selected contacts to CSV format
    var csvContent = "";
    csvContent += "Tag,First Name,Last Name,Company,Department,Job Title,E-mail Address,Email Address 2,Business Phone,Mobile Phone,Business Fax,Birthday,Business Address,Business City,Business State,Business Zip,Business Country,Web Page,Notes\n"; // Add CSV header

    selectedContacts.forEach(function (contact) {
        const replaceNullOrUndefined = (value) => (value === null || value === undefined ? '' : value);
        const rowValues = [
            replaceNullOrUndefined(contact.tag),
            replaceNullOrUndefined(contact.firstName),
            replaceNullOrUndefined(contact.lastName),
            replaceNullOrUndefined(contact.company),
            replaceNullOrUndefined(contact.department),
            replaceNullOrUndefined(contact.jobTitle),
            replaceNullOrUndefined(contact.emailAddress),
            replaceNullOrUndefined(contact.emailAddress2),
            replaceNullOrUndefined(contact.businessPhone),
            replaceNullOrUndefined(contact.mobilePhone),
            replaceNullOrUndefined(contact.businessFax),
            replaceNullOrUndefined(contact.birthday),
            replaceNullOrUndefined(contact.businessAddress),
            replaceNullOrUndefined(contact.businessCity),
            replaceNullOrUndefined(contact.businessState),
            replaceNullOrUndefined(contact.businessZip),
            replaceNullOrUndefined(contact.businessCountry),
            replaceNullOrUndefined(contact.webPage),
            replaceNullOrUndefined(contact.meetDate),
            replaceNullOrUndefined(contact.notes)
        ];
        const quotedRowValues = rowValues.map(value => `"${value}"`);
        csvContent += quotedRowValues.join(',') + '\n';
    });

    // Convert the CSV content to a Blob
    const blob = new Blob([csvContent], { type: 'text/csv' });

    // Create a link element
    const link = document.createElement('a');

    // Set the link's href attribute to a data URL representing the Blob
    link.href = window.URL.createObjectURL(blob);

    // Specify the filename for the download
    link.download = 'contacts.csv';

    // Append the link to the document
    document.body.appendChild(link);

    // Trigger a click on the link to initiate the download
    link.click();

    // Remove the link from the document
    document.body.removeChild(link);
}

//delete selected contacts

function deleteSelectedContacts() {
    var table = document.getElementById("index-table");
    var rows = table.rows;
    var selectedContactIds = [];

    // Iterate through rows and check if the checkbox is selected
    for (var i = 1; i < rows.length; i++) {
        var checkbox = rows[i].getElementsByTagName("input")[0];

        if (checkbox.checked) {
            // Get the contact ID from the corresponding row
            var contactId = rows[i].querySelector('.contact-id-input').value;
            selectedContactIds.push(contactId);
        }
    }

    // Check if any contacts are selected
    if (selectedContactIds.length === 0) {
        alert('Please select contacts to delete.');
        return;
    }

    // Loop through the selected contact IDs and initiate the deletion
    selectedContactIds.forEach(function (contactId) {
        var rowToRemove = document.querySelector('[data-contact-id="' + contactId + '"]');

        if (rowToRemove) {
            // Remove the deleted row from the table
            var tableRow = rowToRemove.parentNode.parentNode;
            tableRow.parentNode.removeChild(tableRow);
        }
        
        var xhr = new XMLHttpRequest();
        xhr.open("DELETE", "/delete_contact/" + contactId, true);

        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                // Optionally handle a successful deletion on the server
            }
        };
        xhr.send();
    });
}

//buttons event listeners
document.addEventListener('DOMContentLoaded', function () {
  var dir = "asc";

  // Attach the copySelectedEmails function to the button click event
  var copyEmailsButton = document.getElementById("copy-emails-button");
  if (copyEmailsButton) {
      copyEmailsButton.addEventListener("click", function () {
          copySelectedEmails();
      });
  }

  // Attach the deleteSelectedContacts function to the button click event
  var deleteSelectedButton = document.getElementById("delete-selected-button");
  if (deleteSelectedButton) {
      deleteSelectedButton.addEventListener("click", function () {
          deleteSelectedContacts();
      });
  }

  var downloadSelectedButton = document.getElementById("download-selected-button");
  if (downloadSelectedButton) {
      downloadSelectedButton.addEventListener("click", function () {
          downloadSelectedContacts();
      });
  }

  // Initial update of the total count
  updateTotalCount();
});