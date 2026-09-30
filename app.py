```python
import streamlit as st
import pandas as pd

# =========================================================
# Basic Settings
# =========================================================

GS1_COMPANY_PREFIX = "08600088840"

st.set_page_config(
    page_title="SSCC-18 / UCC-128 Generator",
    page_icon="📦",
    layout="centered"
)

st.title("SSCC-18 / UCC-128 Generator")
st.caption("For THD DF / Logistic Unit Label")

# =========================================================
# SSCC Check Digit Calculation
# =========================================================

def calculate_check_digit(number_17):
    """
    Calculate GS1 Mod-10 Check Digit.

    number_17 must contain exactly 17 digits.
    """

    if len(number_17) != 17 or not number_17.isdigit():
        raise ValueError("SSCC body must contain exactly 17 digits.")

    total = 0

    # Starting from the rightmost digit,
    # multiply alternately by 3 and 1.
    for i, digit in enumerate(reversed(number_17)):
        digit = int(digit)

        if i % 2 == 0:
            total += digit * 3
        else:
            total += digit

    check_digit = (10 - (total % 10)) % 10

    return str(check_digit)


def generate_sscc(extension_digit, serial_reference):
    """
    Generate SSCC-18.

    Structure:
    Extension Digit (1)
    + GS1 Company Prefix (11)
    + Serial Reference (5)
    + Check Digit (1)
    """

    if not extension_digit.isdigit() or len(extension_digit) != 1:
        raise ValueError("Extension Digit must be exactly 1 digit.")

    serial_reference = str(serial_reference).strip()

    if not serial_reference.isdigit():
        raise ValueError("Serial Reference must contain digits only.")

    if len(serial_reference) > 5:
        raise ValueError("Serial Reference can contain a maximum of 5 digits.")

    # Pad Serial Reference to 5 digits
    serial_reference = serial_reference.zfill(5)

    # 1 + 11 + 5 = 17 digits
    sscc_body = (
        extension_digit
        + GS1_COMPANY_PREFIX
        + serial_reference
    )

    check_digit = calculate_check_digit(sscc_body)

    sscc = sscc_body + check_digit

    return sscc


# =========================================================
# UCC-128
# =========================================================

def generate_ucc128(sscc):
    """
    UCC-128 / GS1-128 data:
    AI (00) + SSCC-18
    """

    if len(sscc) != 18 or not sscc.isdigit():
        raise ValueError("SSCC must contain exactly 18 digits.")

    return "00" + sscc


# =========================================================
# UI
# =========================================================

st.subheader("1. GS1 Information")

st.text_input(
    "GS1 Company Prefix",
    value=GS1_COMPANY_PREFIX,
    disabled=True
)

st.info(
    "Your GS1 Company Prefix is 08600088840 "
    "(11 digits)."
)

# =========================================================
# Single SSCC Generator
# =========================================================

st.subheader("2. Generate SSCC-18")

extension_digit = st.selectbox(
    "Extension Digit",
    options=[str(i) for i in range(10)],
    index=0
)

serial_reference = st.text_input(
    "Serial Reference",
    value="1",
    help="Enter up to 5 digits. Example: 1 → 00001"
)

if st.button("Generate SSCC", type="primary"):

    try:
        sscc = generate_sscc(
            extension_digit,
            serial_reference
        )

        ucc128 = generate_ucc128(sscc)

        st.success("SSCC generated successfully!")

        st.markdown("### SSCC-18")

        st.code(sscc, language=None)

        st.markdown("### UCC-128 / GS1-128 Data")

        st.code(ucc128, language=None)

        st.markdown("### Breakdown")

        serial_padded = str(serial_reference).zfill(5)

        breakdown = f"""
        Extension Digit: `{extension_digit}`

        GS1 Company Prefix: `{GS1_COMPANY_PREFIX}`

        Serial Reference: `{serial_padded}`

        Check Digit: `{sscc[-1]}`

        SSCC-18: `{sscc}`

        UCC-128: `00 + {sscc}`
        """

        st.markdown(breakdown)

    except ValueError as e:
        st.error(str(e))


# =========================================================
# Multiple Pallets
# =========================================================

st.divider()

st.subheader("3. Generate Multiple Pallets")

start_serial = st.number_input(
    "Starting Serial Reference",
    min_value=0,
    max_value=99999,
    value=1,
    step=1
)

pallet_qty = st.number_input(
    "Number of Pallets",
    min_value=1,
    max_value=1000,
    value=1,
    step=1
)

if st.button("Generate Pallet SSCCs"):

    if start_serial + pallet_qty - 1 > 99999:
        st.error(
            "The Serial Reference cannot exceed 99999."
        )

    else:

        rows = []

        for i in range(pallet_qty):

            serial = start_serial + i

            sscc = generate_sscc(
                extension_digit,
                str(serial)
            )

            ucc128 = generate_ucc128(sscc)

            rows.append({
                "Pallet": i + 1,
                "Serial Reference": f"{serial:05d}",
                "SSCC-18": sscc,
                "UCC-128": ucc128
            })

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # CSV download
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="THD_SSCC_UCC128.csv",
            mime="text/csv"
        )
```

### 2. `requirements.txt`

GitHub 建一个文件：

```text
streamlit
pandas
```

### 3. GitHub 文件结构

你的 repository 可以非常简单：

```text
THD-SSCC-Generator/
│
├── app.py
└── requirements.txt
```

然后在 **Streamlit Community Cloud** 里选择这个 GitHub repository，Main file 填：

```text
app.py
```

就可以运行。

---

## 这个版本生成逻辑

以：

```text
Extension Digit = 0
GS1 Company Prefix = 08600088840
Serial Reference = 00001
```

为例：

```text
0
+
08600088840
+
00001
=
00860008884000001
```

这是 **17位 SSCC Body**。

程序再自动计算：

```text
Check Digit
```

最终得到：

```text
SSCC-18
```

然后自动加：

```text
AI (00)
```

得到：

```text
UCC-128 = 00 + SSCC-18
```

---

### 不过我建议你下一版直接做成 **THD DF 专用 Label Generator**

因为你现在不是单纯为了算数字，而是要实际用于 **THD DF shipment**。

我可以给你把这个 Streamlit 做成：

**输入 PO + Carton/Pallet 数量 → 自动生成 SSCC → 自动生成 Code 128 条码 → 自动生成 THD UCC-128 Pallet Label → 一键下载 PDF 打印。**

比如直接生成这种：

```text
┌─────────────────────────────────────┐
│             THD DF                  │
│                                     │
│ PO: 233073092                       │
│ Pallet: 1 of 2                      │
│                                     │
│       █████████████████             │
│       █  Code 128   █               │
│       █████████████████             │
│                                     │
│ 000860008884000001X                 │
│                                     │
│ SSCC-18: 00860008884000001X         │
└─────────────────────────────────────┘
```

这样你们仓库就可以**直接下载 PDF → 打印 → 贴到 Pallet 上**，比单纯生成 SSCC 数字实用很多。
