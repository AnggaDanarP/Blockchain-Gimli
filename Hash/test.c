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

int main(void)
{
    char string1[] = "There's plenty for the both of us, may the best Dwarf win.";
    printf(print_hex(string1));
    return 0;
}