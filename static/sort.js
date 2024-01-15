// Sorting table columns with JavaScript and HTML5 using Chinese Radical and Stroke Count
document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('index-table');
    const headers = table.querySelectorAll('th');
    const tableBody = table.querySelector('tbody');
    const rows = tableBody.querySelectorAll('tr');

    // Track sort directions
    const directions = Array.from(headers).map(function (header) {
        return '';
    });

    // 获取汉字的部首
    const getRadical = function (ch) {
        const charCode = ch.charCodeAt(0);
        const radicalCode = Math.floor((charCode - 0x4e00) / 0x100);
        return String.fromCharCode(0x4e00 + radicalCode);
    };

    // 获取汉字的笔画数
    const getStrokeCount = function (ch) {
        const charCode = ch.charCodeAt(0);
        return cnchar.stroke(ch);
    };

    const transform = function (index, content) {
        const type = headers[index].getAttribute('data-type');
        switch (type) {
            case 'number':
                return parseFloat(content);
            case 'string':
            default:
                return content;
        }
    };

    const sortColumn = function (index) {
        const direction = directions[index] || 'asc';
        const multiplier = direction === 'asc' ? 1 : -1;

        const newRows = Array.from(rows);

        newRows.sort(function (rowA, rowB) {
            const cellA = rowA.querySelectorAll('td')[index].innerHTML;
            const cellB = rowB.querySelectorAll('td')[index].innerHTML;

            const a = transform(index, cellA);
            const b = transform(index, cellB);

            // 修改比较逻辑以按照部首和笔画进行排序
            const radicalA = getRadical(a);
            const radicalB = getRadical(b);

            if (radicalA === radicalB) {
                const strokeA = getStrokeCount(a);
                const strokeB = getStrokeCount(b);
                return (strokeA - strokeB) * multiplier;
            } else {
                return (radicalA.localeCompare(radicalB)) * multiplier;
            }
        });

        [].forEach.call(rows, function (row) {
            tableBody.removeChild(row);
        });

        directions[index] = direction === 'asc' ? 'desc' : 'asc';

        newRows.forEach(function (newRow) {
            tableBody.appendChild(newRow);
        });
    };

    [].forEach.call(headers, function (header, index) {
        header.addEventListener('click', function () {
            sortColumn(index);
        });
    });
});
