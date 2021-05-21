

typedef union UnionA
{
    char bytes[4];
    float a;
} UnionA;

typedef enum EnumA
{
    EnumA__val_1=1,
    EnumA__val_2=0,
    EnumA__val_3=5,
} EnumA;

typedef struct StructA {
    char a;
    int b;
} StructA;

typedef struct StructB {
    char a[100];
} StructB;

typedef struct StructC {
    StructA a;
    StructB b;
} StructC;

typedef struct StructD {
    StructA a[10];
} StructD;

typedef struct StructE {
    char a: 4;
    char b: 4;
} StructE;

typedef struct StructF
{
    char a[5][10];
} StructF;

typedef struct StructG
{
    char a[5][4][3][2];
} StructG;

typedef struct StructH
{
    char* a;
} StructH;

typedef struct StructI
{
    char** a;
} StructI;

typedef struct StructJ
{
    StructI** a;
} StructJ;

EnumA enum_a;

UnionA union_a;

StructA struct_a;
StructB struct_b;
StructC struct_c;
StructD struct_d;
StructE struct_e;
StructF struct_f;
StructG struct_g;
StructH struct_h;
StructI struct_i;
StructJ struct_j;
