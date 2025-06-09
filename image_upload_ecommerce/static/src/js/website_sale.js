import { WebsiteSale } from '@website_sale/js/website_sale';

WebsiteSale.include({

    init() {
        this._super(...arguments);
    },

    async _addToCartInPage(params) {
        const data = await this._super(params);
        this._uploadCustomImage(data.line_id);
        return data;
    },

    _onConfigured(options, values) {
        this._uploadCustomImage(values.line_id);
        return this._super(...arguments);
    },

    async _uploadCustomImage(line_id) {
        const fileInput = document.querySelector('input[name="custom_image"]');
        const fileName = document.getElementById('fileName');
        const errorBox = document.getElementById("o_wsale_errors");
        const file = fileInput?.files?.[0];

        if (file && line_id) {
            try {
                const base64Image = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result.split(',')[1]);
                    reader.onerror = () => reject("File read error");
                    reader.readAsDataURL(file);
                });

                $.ajax({
                    type: 'POST',
                    url: '/website/action/add_custom_image',
                    data: {
                        image: base64Image,
                        line_id: line_id,
                        csrf_token: window.csrf_token,
                        token: window.csrf_token,
                    },
                    error: function (xhr, status, error) {
                        if (errorBox) {
                            errorBox.textContent = `Image upload failed: ${error}`;
                            errorBox.classList.remove("d-none");
                        }
                    }
                });
                if (fileInput) fileInput.value = '';
                if (fileName) fileName.value = '';

            } catch (error) {
                if (errorBox) {
                    errorBox.textContent = `Failed to upload custom image: ${error}`;
                    errorBox.classList.remove("d-none");
                }
            }
        }
    }

});
