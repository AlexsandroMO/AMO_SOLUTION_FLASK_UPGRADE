
//Mostrar
$('#passar_mouse1').mouseover(function(){
    $('#mostrar1').css('display', 'block');
  });
  
  $('#passar_mouse1').mouseout(function(){
    $('#mostrar1').css('display', 'none');
  });

$('#passar_mouse2').mouseover(function(){
    $('#mostrar2').css('display', 'block');
  });
  
  $('#passar_mouse2').mouseout(function(){
    $('#mostrar2').css('display', 'none');
  });


  //-----
  var lista = [
    ["0,5", 14.5000, 0.1100],
    ["1", 19.5000, 0.3100],
    ["1,5", 13.3000, 0.4100],
    ["2,5", 7.9800, 0.4100],
    ["4", 4.9500, 0.5100],
    ["6", 3.3000, 0.5100],
    ["10", 1.9100, 0.5100],
    ["16", 1.2100, 0.6100],
    ["25", 0.7800, 0.6100],
    ["35", 0.5540, 0.6800],
    ["50", 0.3860, 0.6800],
    ["70", 0.2720, 0.6800],
    ["95", 0.2060, 0.6800],
    ["120", 0.1610, 0.6800],
    ["150", 0.1290, 0.8600],
    ["185", 0.1000, 0.8600],
    ["240", 0.0801, 0.8600],
    ["300", 0.0641, 0.8600]
];

console.log(lista);

//------------
let cableR = document.getElementById("cableR");
let cableX = document.getElementById("cableX");

let elementSected = document.getElementById("sectionChoise");

console.log("Cable: ", cableR, cableX, elementSected);

elementSected.addEventListener("change", function () {
    let selectedValue = elementSected.value;
    let varCol1, varCol2;

    for (var i = 0; i < lista.length; i++) {
        var sublista = lista[i];
        var varCol0 = sublista[0];

        if (varCol0 === selectedValue) {
            varCol1 = sublista[1];
            varCol2 = sublista[2];
            break;
        }
    }

    console.log("A: ", varCol1);
    console.log("B: ", varCol2);

    cableR.value = varCol1;
    cableX.value = varCol2;

    console.log("Valor da coluna 1: " + selectedValue);
});



function calcCirc() {
    let circuitType = document.getElementById("circuit-type").value;
    let nominalTension = parseFloat(document.getElementById("nominalTension").value);
    let nominalCorrent = parseFloat(document.getElementById("nominalCorrent").value);
    let Corrent = document.getElementById("nominalCorrent");
    let powerCircuit = parseFloat(document.getElementById("powerCircuit").value);
    let potencialFactor = parseFloat(document.getElementById("potencialFactor").value);
    let dimensionCorrent = document.getElementById("dimensionCorrent");
    let dropTension = parseFloat(document.getElementById("dropTension").value);
    let circuitLenght = parseFloat(document.getElementById("circuitLenght").value);
    let cableR = parseFloat(document.getElementById("cableR").value);
    let cableX = parseFloat(document.getElementById("cableX").value);
    let cableFase = parseFloat(document.getElementById("cableFase").value);
    let dropTensionE = document.getElementById("dropTensionE");
    let readCorrent = 0;

    // Lógica para calcular a corrente ou a potência
    if (powerCircuit > 0 && nominalTension > 0) {
        // Calcular corrente a partir da potência
        readCorrent = (powerCircuit / nominalTension).toFixed(2);
        Corrent.value = readCorrent;
    } else if (nominalCorrent > 0) {
        // Calcular potência a partir da corrente
        powerCircuit = (nominalCorrent * nominalTension).toFixed(2);
        document.getElementById("powerCircuit").value = powerCircuit;
        readCorrent = nominalCorrent.toFixed(2);
        Corrent.value = readCorrent;
    } else {
        // Se não houver dados suficientes, retornar
        console.warn("Por favor, forneça a potência ou a corrente nominal.");
        return;
    }

    let idim = (readCorrent * 0.37) + Number(readCorrent);
    let A = readCorrent;

    console.log('>>>>>>>>>>> |   >>>>>>> : ', A, idim, Number(A) + Number(idim));

    let result1 = 2 * parseFloat(idim) * (cableR * potencialFactor + cableX * Math.sin(Math.acos(potencialFactor))) * circuitLenght / 100 / cableFase / (nominalTension / 10);
    let result2 = Math.sqrt(3) * idim * (cableR * potencialFactor + cableX * Math.sin(Math.acos(potencialFactor))) * circuitLenght / 100 / cableFase / (nominalTension / 10);

    console.log('>>>>>: ', circuitType, nominalTension);
    console.log('Result: ', result1.toFixed(2), result2.toFixed(2));

    dimensionCorrent.value = parseFloat(idim);
    dropTensionE.style.fontWeight = "bold";
    dropTensionE.style.color = "rgb(255, 255, 255)";

    if (circuitType == 'Single-Phase') {
        dropTensionE.value = result1.toFixed(2);
        console.log('Foi aqui no Mono');
        dropTensionE.style.backgroundColor = result1 < dropTension ? "rgb(41, 154, 45)" : "rgb(255, 1, 69)"; // verde ou vermelho
    }
    if (circuitType == 'T Single-phase') {
        console.log('Foi aqui no Tri');
        dropTensionE.value = result2.toFixed(2);
        dropTensionE.style.backgroundColor = result2 < dropTension ? "rgb(41, 154, 45)" : "rgb(255, 1, 69)"; // verde ou vermelho
    }
}
