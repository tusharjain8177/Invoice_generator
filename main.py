from flask import Flask, render_template, request, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# Directory to store templates (can be expanded for user uploads)
TEMPLATE_DIR = 'templates/invoice_templates'
os.makedirs(TEMPLATE_DIR, exist_ok=True)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate_invoice():
    if request.method == 'POST':
        # Get form data
        customer_name = request.form['customer_name']
        items = request.form.getlist('item[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        invoice_number = request.form['invoice_number']
        date = request.form['date']

        # Load the template image
        template_path = 'Template.jpeg'  # Replace with your template image path
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        # Replace 'arial.ttf' with your font file and adjust size
        font = ImageFont.truetype('arial.ttf', size=20)

        # Map data to positions on the template
        draw.text((300, 440), f"{invoice_number}", fill="black", font=font)
        draw.text((300, 350), f"{date}", fill="black", font=font)
        draw.text((700, 350), f"{customer_name}", fill="black", font=font)
        # draw.text((100, 100), f"Customer Address: {customer_address}", fill="black", font=font)

        # Headers for items section
        # draw.text((100, 750), "S.No", fill="black", font=font)
        # draw.text((300, 700), "Item", fill="black", font=font)
        # draw.text((600, 700), "Qty", fill="black", font=font)
        # draw.text((700, 750), "Price", fill="black", font=font)
        # draw.text((900, 700), "Total", fill="black", font=font)

        # Add items to the invoice
        y = 680
        grand_total = 0
        for i, (item, qty, price) in enumerate(zip(items, quantities, prices), start=1):
            total = int(qty) * float(price)
            grand_total += total
            draw.text((150, y), f"{i}", fill="black", font=font)
            draw.text((300, y), item, fill="black", font=font)
            draw.text((620, y), qty, fill="black", font=font)
            draw.text((720, y), f"{price}", fill="black", font=font)
            draw.text((900, y), f"{total:.2f}", fill="black", font=font)
            y += 20

        # Add grand total
        # draw.text((700, y), "Grand Total:", fill="black", font=font)
        draw.text((900, 1105), f"{grand_total:.2f}", fill="black", font=font)

        # Add signature if uploaded
        if 'signature' in request.files:
            signature_file = request.files['signature']
            if signature_file.filename != '':
                signature_img = Image.open(signature_file)
                # Resize the signature if needed
                signature_img = signature_img.resize(
                    (150, 50))  # Adjust size as needed
                # Paste the signature onto the invoice
                # Adjust position as needed
                img.paste(signature_img, (750, 1150), mask=signature_img)

        # Save image to buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="invoice.png", mimetype='image/png')

    return render_template('generate.html')


@app.route('/template', methods=['GET', 'POST'])
def edit_template():
    if request.method == 'POST':
        template_name = request.form['template_name']
        template_content = request.form['template_content']
        template_path = os.path.join(TEMPLATE_DIR, f"{template_name}.html")

        with open(template_path, 'w') as f:
            f.write(template_content)

        return f"Template '{template_name}' saved successfully!"

    return render_template('edit_template.html')


@app.route('/find_positions', methods=['GET', 'POST'])
def find_positions():
    if request.method == 'POST':
        template_path = 'Template.jpeg'  # Replace with your template image path
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)

        # Draw a coordinate grid on the template
        for x in range(0, img.width, 50):
            draw.line([(x, 0), (x, img.height)], fill="gray", width=1)
        for y in range(0, img.height, 50):
            draw.line([(0, y), (img.width, y)], fill="gray", width=1)

        # Optionally label coordinates
        font = ImageFont.load_default()
        for x in range(0, img.width, 100):
            for y in range(0, img.height, 100):
                draw.text((x + 5, y + 5),
                          f"({x},{y})", fill="black", font=font)

        # Save image to buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="coordinate_grid.png", mimetype='image/png')

    return render_template('find_positions.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
