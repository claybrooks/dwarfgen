#include <array>

typedef struct StdArrayStruct
{
    std::array<char, 4> a;
} StdArrayStruct;
StdArrayStruct stdArrayStruct;

typedef union UnionA
{
    char bytes[4];
    float a;
} UnionA;

typedef enum class EnumA
{
    val_1,
    val_2,
    val_3,
} EnumA;

typedef enum class EnumB
{
    val_1=1,
    val_2=0,
    val_3=5,
} EnumB;

typedef enum EnumC
{
    EnumC__val_1=1,
    EnumC__val_2=0,
    EnumC__val_3=5,
} EnumC;

typedef struct StructA {
    char a;
    int b;
} StructA;

typedef struct StructB {
    char a[100];
} StructB;

namespace Namespace
{
    typedef struct StructC {
        char a;
        int b;
    } StructC;

    namespace InnerNamespace
    {
        typedef struct StructD {
            char a[100];
        } StructD;
    }
}

typedef struct StructE {
    StructA a;
    StructB b;
} StructE;

typedef struct StructF {
    StructA a[10];
} StructF;

typedef struct StructG {
    Namespace::StructC a;
} StructG;

typedef struct StructH {
    Namespace::StructC a[10];
} StructH;

namespace Namespace
{
    typedef struct StructI {
        Namespace::InnerNamespace::StructD a;
    } StructI;

    typedef struct StructJ {
        Namespace::InnerNamespace::StructD a[2];
    } StructJ;
}

typedef struct StructK {
    char a: 4;
    char b: 4;
} StructK;

typedef struct StructL {
private:
    char a;
protected:
    char b;
public:
    char c;
} StructL;

template<typename T, typename Q>
struct StructM {
    T a;
    Q b;
};

class ClassA
{
    char a;
protected:
    char b;
public:
    char c;
};

class ClassB
{
public:
    static char a;
    char b;
};

class ClassC
{
    static ClassA a;
protected:
    static ClassB b;
public:
    static int c;
};

class ClassD
{
protected:
    static Namespace::InnerNamespace::StructD a;
public:
    Namespace::InnerNamespace::StructD b;
};

typedef struct StructN {
    char a;
    int b;
} StructN;

typedef struct StructNDerived: public StructN {
    char c;
    int d;
} StructNDerived;

typedef struct StructNDerivedPrivate: private StructN {
    char c;
    int d;
} StructNDerivedPrivate;

typedef struct StructNDerivedProtected: protected StructN {
    char c;
    int d;
} StructNDerivedProtected;

typedef struct StructN_2 {
    char a;
    int b;
} StructN_2;

typedef struct StructNMultiDerived: public StructN, StructN_2 {
    char c;
    int d;
} StructNMultiDerived;

typedef struct StructNMultiDerivedMixAccessibility: public StructN, private StructN_2 {
    char c;
    int d;
} StructNMultiDerivedMixAccessibility;

typedef struct StructWithEnum {
    EnumA a;
} StructWithEnum;

typedef struct StructO
{
    char a[5][10];
} StructO;

typedef struct StructP
{
    char a[5][4][3][2];
} StructP;

typedef struct StructQ
{
    char* a;
} StructQ;

typedef struct StructR
{
    StructR(char* in): a(*in){}
    char& a;
} StructR;

typedef struct StructS
{
    char** a;
} StructS;

typedef struct StructT
{
    StructS* a;
} StructT;

typedef struct StructU
{
    StructU(char* pA): a(pA) {}
    char*& a;
} StructU;

typedef struct StructV
{
    StructV(char*** pA): a(pA) {}
    char***& a;
} StructV;

UnionA union_a;

StructA struct_a;
StructB struct_b;
Namespace::StructC struct_c;
Namespace::InnerNamespace::StructD struct_d;
StructE struct_e;
StructF struct_f;
StructG struct_g;
StructH struct_h;
Namespace::StructI struct_i;
Namespace::StructJ struct_j;
StructK struct_k;
StructL struct_l;
StructM<char, int> struct_m;
StructNDerived struct_n_derived;
StructNDerivedPrivate struct_n_derived_private;
StructNDerivedProtected struct_n_derived_protected;
StructNMultiDerived struct_n_multi_derived;
StructNMultiDerivedMixAccessibility structd_n_multi_derived_mix_accessibility;
StructO struct_o;
StructP struct_p;
StructQ struct_q;
StructS struct_s;
StructT struct_t;

char t;
StructR struct_r(&t);

char a = 'a';
char* pA = &a;
char** ppA = &pA;
char*** pppA = &ppA;
StructU struct_u(pA);
StructV struct_v(pppA);

StructWithEnum structWithEnum;

ClassA class_a;
ClassB class_b;
ClassC class_c;
ClassD class_d;

EnumA enum_a;
EnumB enum_b;
EnumC enum_c;