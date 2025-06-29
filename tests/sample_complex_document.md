# 🚀 Complete Development Guide - International Project

This is a complete documentation that includes multiple languages, emojis, complex numbering, and edge cases to test the markdown-section-splitter.

## 1. Initial Setup 📋

This is the first step to configure our project. It includes basic configuration and environment preparation.

### 1.1. System Requirements

- Python 3.6+
- Git installed
- Code editor

### 1.2. Dependency Installation

```bash
pip install requirements.txt
npm install
```

#### 1.2.1. Installation Verification

Run the following commands to verify:

```python
import sys
print(f"Python version: {sys.version}")
```

## 1.3. Advanced Configuration (Incorrect Numbering)

This section has intentionally incorrect numbering to test the splitter.

### 1.3.1. Environment Variables

Configure the following variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `DEBUG_MODE`

## 4. Development and Testing 🛠️ (Numbering Jump)

We intentionally jump from 1.3 to 4 to test edge cases.

### 4.1. Project Structure

```text
project/
├── src/
├── tests/
└── docs/
```

### 4.2. Development Flow

1. Create feature branch
2. Develop functionality
3. Write tests
4. Create pull request

#### 4.2.3. Without 4.2.1 or 4.2.2 (Triple Jump)

This subsection skips numbers to test edge cases.

## русский раздел (Russian Section)

Этот раздел написан на русском языке для тестирования поддержки кириллицы.

### Подраздел на русском

Содержимое подраздела с кириллическими символами.

## 中文部分 (Chinese Section)

这个部分是用中文写的，用来测试中文字符的支持。

### 中文子部分

中文内容用于测试Unicode支持。

## Ελληνικό Τμήμα (Greek Section)

Αυτό το τμήμα είναι γραμμένο στα ελληνικά για να δοκιμάσουμε την υποστήριξη ελληνικών χαρακτήρων.

## Configuration & Architecture

Section with special characters in the title: &, which should be handled correctly.

### API Design

The API follows REST principles:

- GET /api/users
- POST /api/users
- PUT /api/users/{id}
- DELETE /api/users/{id}

## FAQ's and Frequently Asked Questions ❓

This section contains apostrophes and question marks.

### How does the system work?

The system works as follows...

### What happens if there are errors?

In case of errors, the system...

## Performance & Optimization ⚡🔧

This section has multiple emojis and special symbols.

### Performance Metrics

- Response time: < 200ms
- Throughput: > 1000 req/s
- Availability: 99.9%

## 3.2.1. Section with Incorrect Level Format

This should be a level 2 section (##) but has level 3 numbering.

## 0. Special Section with Zero

Numbering from zero to test edge cases.

## Deploy & Production 🌐

Production deployment process.

### CI/CD Pipeline

```yaml
stages:
  - build
  - test
  - deploy
```

#### Docker Configuration

```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
```

## Troubleshooting 🐛 & Debug 🔍

Section for problem resolution.

### Common Issues

1. **Connection error**: Check network
2. **Timeout**: Increase time limit
3. **Memory leak**: Review garbage collection

## API Reference (v2.0) - Links 🔗

Complete API documentation version 2.0.

### Authentication

```http
POST /auth/login
Authorization: Bearer <token>
```

### Main Endpoints

#### Users

```http
GET /api/v2/users
POST /api/v2/users
```

#### Products

```http
GET /api/v2/products
POST /api/v2/products
```

## C++ / Python Integration 🐍

Integration between C++ and Python for performance.

### Binding with pybind11

```cpp
#include <pybind11/pybind11.h>

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(example, m) {
    m.def("add", &add, "A function which adds two numbers");
}
```

## $$ Costs and Pricing €€

Information about costs in different currencies.

### Subscription Plans

- **Basic**: $9.99/month
- **Pro**: €19.99/month  
- **Enterprise**: $99.99/month

## Header with **bold** and *italic* text

This header contains markdown formatting to test edge cases.

### Header with `code` in it

```python
def test_function():
    pass
```

## Header with [link](http://example.com)

This header contains a markdown link.

## Header with <em>HTML</em> tags

This header contains HTML tags to test filtering.

## 100% Coverage ✅ Testing

Final section with percentages and verification emojis.

### Quality Metrics

- **Test Coverage**: 100% ✅
- **Linting**: Passing ✅  
- **Security Scan**: Clean ✅
- **Performance**: Optimal ⚡

### Conclusions

This complex documentation allows testing all edge cases of the markdown-section-splitter:

1. Disordered numbering with jumps
2. Unicode characters from multiple languages
3. Emojis in different positions
4. Special characters and symbols
5. Markdown formatting in headers
6. HTML in headers
7. Links in headers
8. Complex header hierarchy
9. Code blocks with different languages
10. Edge cases of numbering (0, large jumps)

The splitter should handle all these cases correctly!

## Code Block with Fake Headers

```markdown
# This is not a real header
## Neither is this
### Nor this one
```

This block contains fake headers that should NOT be detected as real sections.

## 15. Final Section with High Number

Last section with a very large numerical jump to test edge cases.

### Final Summary

The complete document includes all the test cases necessary to validate the behavior of the markdown-section-splitter in real and complex scenarios.
