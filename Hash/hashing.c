#define PY_SSIZE_T_CLEAN
#include <C:\Users\Angga Danar\AppData\Local\Programs\Python\Python310\include\Python.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "gimli_hash.c"

char final[32];

char* print_hex(char* string){
    uint8_t output[32];
    Gimli_hash(string, strlen(string), output, 32);
    
    char hexstr[32][2 + 1] = {0};
    const char hex[16] = "0123456789abcdef";
    memset(hexstr, ' ', sizeof(hexstr));

    for (size_t i = 0; i < 32; i++) {
        hexstr[i][0] = hex[(output[i] & 0xf0) >> 4];
        hexstr[i][1] = hex[(output[i] & 0x0f)];
        memcpy(final, hexstr, sizeof(hexstr));
    }
    return final;
}

static PyObject * hash(PyObject *self, PyObject *args) {
    PyObject* str;
    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    return PyUnicode_FromString(print_hex(str));
}

static PyMethodDef hashMethods[] = {
    {"gimli", (PyCFunction)hash, METH_VARARGS, "Gimli Algorithm Hash"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef hashModule = {
    PyModuleDef_HEAD_INIT,
    "hash_module", 
    NULL,
    -1,
    hashMethods
};

PyMODINIT_FUNC PyInit_hash(void) {
    return PyModule_Create(&hashModule);
}
