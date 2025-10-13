(function () {
    const DEFAULT_MIN_LENGTH = 2;
    const DEFAULT_MAX_RESULTS = 15;
    const CONTAINER_SELECTOR = '[data-autocomplete]';

    // Debounce function to limit function calls
    const debounce = (fn, delay = 200) => {
        let timer = null;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), delay);
        };
    };

    // If the value is an array, return it; otherwise, return an empty array
    const toArray = (value) => (Array.isArray(value) ? value : []);

    // Update the input field's value based on the selected options in the dropdown
    const updateInputFromSelect = (select, input) => {
        // If neither select nor input exist, do nothing
        if (!select || !input) {
            return;
        }

        // Get content of the selected options
        const text = Array.from(select.selectedOptions)
            // Extract and trim text content
            .map((option) => option.textContent?.trim())
            // Remove empty values
            .filter(Boolean)
            // Join with commas
            .join(', ');

        // Update the input field's value
        input.value = text;
    };

    // Create a button element for each autocomplete result item
    const createResultItem = (item, onSelect) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'w-full text-left px-3 py-2 text-sm hover:bg-primary/10 focus:bg-primary/20 focus:outline-none flex flex-col gap-1';

        // Create and append label span
        const label = document.createElement('span');
        // In case there is no label, use an empty string
        label.textContent = item.label ?? '';
        button.appendChild(label);

        // If the json item has something in its description field, 
        // create and append an span
        if (item.description) {
            const description = document.createElement('span');
            description.className = 'text-xs text-foreground/60';
            description.textContent = item.description;
            button.appendChild(description);
        }

        button.addEventListener('click', () => onSelect(item));
        return button;
    };

    const fetchMatches = (url, query, maxResults) => {
        const endpoint = `${url}?q=${encodeURIComponent(query)}`;
        return fetch(endpoint, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then((response) => (response.ok ? response.json() : []))
            .then((data) => toArray(data).slice(0, maxResults))
            .catch(() => []);
    };

    const applySelection = ({ item, select, hiddenInput, allowMultiple }) => {
        if (select) {
            let option = Array.from(select.options).find((opt) => opt.value === String(item.id));

            if (!option) {
                option = new Option(item.label ?? '', item.id, true, true);
                select.appendChild(option);
            }

            if (allowMultiple) {
                option.selected = true;
            } else {
                Array.from(select.options).forEach((opt) => {
                    opt.selected = opt === option;
                });
            }

            select.dispatchEvent(new Event('change', { bubbles: true }));
        }

        if (hiddenInput) {
            hiddenInput.value = item.id;
            hiddenInput.dataset.autocompleteLabel = item.label ?? '';
        }
    };

    const resetSelection = ({ select, hiddenInput, input }) => {
        if (select) {
            Array.from(select.options).forEach((opt) => {
                opt.selected = false;
            });
            select.dispatchEvent(new Event('change', { bubbles: true }));
        }

        if (hiddenInput) {
            hiddenInput.value = '';
            delete hiddenInput.dataset.autocompleteLabel;
        }

        if (input) {
            input.value = '';
        }
    };

    const initContainer = (container) => {
        if (!container || container.dataset.autocompleteReady === 'true') {
            return;
        }

        const url = container.dataset.autocompleteUrl;
        if (!url) {
            return;
        }

        const minLength = parseInt(container.dataset.autocompleteMinLength || DEFAULT_MIN_LENGTH, 10);
        const maxResults = parseInt(container.dataset.autocompleteMaxResults || DEFAULT_MAX_RESULTS, 10);
        const autoSubmit = container.dataset.autocompleteAutoSubmit === 'true';

        const input = container.querySelector('[data-autocomplete-input]');
        const results = container.querySelector('[data-autocomplete-results]');
        const select = container.querySelector('[data-autocomplete-select]');
        const hiddenInput = container.querySelector('[data-autocomplete-value]');
        const clearButton = container.querySelector('[data-autocomplete-clear]');

        if (!input || !results) {
            return;
        }

        const allowMultiple = Boolean(select?.multiple);

        if (select) {
            select.classList.add('hidden');
        }

        const closeResults = () => {
            results.classList.add('hidden');
        };

        const renderResults = (items, onSelect) => {
            results.innerHTML = '';

            if (!items.length) {
                const empty = document.createElement('div');
                empty.className = 'px-3 py-2 text-sm text-foreground/60';
                empty.textContent = 'Sin resultados';
                results.appendChild(empty);
                results.classList.remove('hidden');
                return;
            }

            items.forEach((item) => {
                results.appendChild(createResultItem(item, onSelect));
            });

            results.classList.remove('hidden');
        };

        const handleSelect = (item) => {
            applySelection({ item, select, hiddenInput, allowMultiple });
            if (select) {
                updateInputFromSelect(select, input);
            } else {
                input.value = item.label ?? '';
            }
            closeResults();

            if (autoSubmit && input.form) {
                input.form.submit();
            }
        };

        const debouncedSearch = debounce((term) => {
            const query = term.trim();
            if (query.length < minLength) {
                closeResults();
                return;
            }

            fetchMatches(url, query, maxResults).then((items) => {
                renderResults(items, handleSelect);
            });
        });

        input.addEventListener('input', (event) => {
            debouncedSearch(event.target.value || '');
        });

        input.addEventListener('focus', () => {
            const current = input.value.trim();
            if (current.length >= minLength) {
                debouncedSearch(current);
            }
        });

        input.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeResults();
            }
        });

        if (clearButton) {
            clearButton.addEventListener('click', () => {
                resetSelection({ select, hiddenInput, input });
                closeResults();
            });
        }

        document.addEventListener('click', (event) => {
            if (!container.contains(event.target)) {
                closeResults();
            }
        });

        if (select) {
            updateInputFromSelect(select, input);
        } else if (hiddenInput && hiddenInput.value) {
            input.value = hiddenInput.dataset.autocompleteLabel || '';
        }

        container.dataset.autocompleteReady = 'true';
    };

    const initAll = (selector = CONTAINER_SELECTOR) => {
        document.querySelectorAll(selector).forEach((container) => initContainer(container));
    };

    if (!window.UClases) {
        window.UClases = {};
    }

    window.UClases.Autocomplete = {
        init: initAll,
        initOne: initContainer,
    };

    document.addEventListener('DOMContentLoaded', () => {
        initAll();
    });
})();