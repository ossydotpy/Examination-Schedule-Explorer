function generateTableHtml(title, tableContent) {
    return (
        '<h2>' + title + '</h2>' +
        (tableContent.find('tr').length > 0
            ? '<table>' + tableContent.html() + '</table>'
            : '<p>No ' + title.toLowerCase() + ' examinations found.</p>'
        )
    );
}

$(document).ready(function () {
    $('#printButton').on('click', function () {
        // Get the table content from each card
        var majorTable = $('#major-card table').clone();
        var minorTable = $('#minor-card table').clone();
        var facultyTable = $('#faculty-card table').clone();

        majorTable.find('tr').each(function () {
            $(this).find('td:eq(4), th:eq(4)').remove();
        });
        minorTable.find('tr').each(function () {
            $(this).find('td:eq(4), th:eq(4)').remove();
        });
        facultyTable.find('tr').each(function () {
            $(this).find('td:eq(4), th:eq(4)').remove();
        });

        var printWindow = window.open('', '_blank');
        printWindow.document.open();
        printWindow.document.write('<html><head><title>Your Personalised Timetable</title>' +
            '<style>' +
            'body { font-family: "Courier New", monospace; background-color: #000; color: #ccc; }' +
            'table { width: 100%; margin-bottom: 20px; border-collapse: collapse; }' +
            'th, td { text-align: left; padding: 8px; border: 1px dashed #ccc; }' +
            'th { background-color: #333; }' +
            'td { border-top: 1px dashed #ccc; }' +
            'h1 { border-bottom: 1px dashed #ccc; padding-bottom: 5px; }' +
            '</style></head><body>' +
            generateTableHtml('Examination Timetable', majorTable) +

            '</body></html>');
        printWindow.document.close();

        printWindow.print();
        printWindow.close();
    });
});

// more exams page js
