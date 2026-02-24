# Copyright SandboxAQ 2021-2024.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tools for performing Bravyi-Kitaev Transformation, as prescribed via the
Fenwick Tree mapping. This implementation accommodates mapping of qubit
registers where the number of qubits is not a power of two.

NB: this is a minimal implementation, just wrapping around current openfermion
code (v 1.0.1). This wrapper enables future refactoring to utilize our own
implementation, as needed.
"""

from openfermion.utils import count_qubits
# from openfermion.transforms import bravyi_kitaev as openfermion_bravyi_kitaev

from qiskit_nature.second_q.mappers import BravyiKitaevMapper  # , BravyiKitaevSuperFastMapper
from qiskit_nature.second_q.operators import FermionicOp

from tangelo.linq.translator.translate_qiskit import translate_op_from_qiskit


# openfermion implementace

# def bravyi_kitaev(fermion_operator, n_qubits):
#     """Execute transformation of FermionOperator to QubitOperator using the
#     Bravyi-Kitaev transformation. Important note: there are several
#     implementations of "Bravyi Kitaev" transformation, in both the literature,
#     and historical versions of openfermion. This function executes the
#     transformaton defined in arXiv:quant-ph/0003137. Different versions are not
#     necessarily the same, and result in undesirable performance. This method is
#     a simple wrapper around openfermion's bravyi_kitaev, but we are forcing the
#     user to pass n_qubits to avoid unexpected behaviour.

#     Args:
#         fermion_operator (FermionOperator): input fermionic operator to be
#             transformed.
#         n_qubits (int): number of qubits associated with the operator.

#     Returns:
#         QubitOperator: output bravyi-kitaev encoded qubit operator.
#     """
#     if not (type(n_qubits) is int):
#         raise TypeError("Number of qubits (n_qubits) must be integer type.")
#     if n_qubits < count_qubits(fermion_operator):
#         raise ValueError("Invalid (too few) number of qubits (n_qubits) for input operator.")

#     qubit_operator = openfermion_bravyi_kitaev(fermion_operator, n_qubits=n_qubits)

#     return qubit_operator


def bravyi_kitaev(fermion_operator, n_qubits):
    """Execute transformation of FermionOperator to QubitOperator using the
    Bravyi-Kitaev transformation. Important note: there are several
    implementations of "Bravyi Kitaev" transformation, in both the literature,
    and historical versions of openfermion. This function executes the
    transformaton defined in arXiv:quant-ph/0003137. Different versions are not
    necessarily the same, and result in undesirable performance. This method is
    a simple wrapper around openfermion's bravyi_kitaev, but we are forcing the
    user to pass n_qubits to avoid unexpected behaviour.

    Args:
        fermion_operator (FermionOperator): input fermionic operator to be
            transformed.
        n_qubits (int): number of qubits associated with the operator.

    Returns:
        QubitOperator: output bravyi-kitaev encoded qubit operator.
    """
    if not (type(n_qubits) is int):
        raise TypeError("Number of qubits (n_qubits) must be integer type.")
    if n_qubits < count_qubits(fermion_operator):
        raise ValueError("Invalid (too few) number of qubits (n_qubits) for input operator.")

    # klic je ve formatu tuple: ((27, 1), (27, 1), (27, 0), (27, 0))
    # preklad termu do tvaru pro qiskit
    # https://qiskit-community.github.io/qiskit-nature/stubs/qiskit_nature.second_q.operators.FermionicOp.html#qiskit_nature.second_q.operators.FermionicOp
    # print(fermion_operator.terms[((27, 1), (27, 1), (27, 0), (27, 0))])
    # print(fermion_operator.__dict__.keys())

    # taky by asi slo pouzit: https://quantumai.google/reference/python/openfermion/transforms ale uz nejak neverim openfermionu
    # BKFS: The number of qubits is generally defined by the number of edges (in the fermionic interaction graph, making it rather than for particles.
    # TOTO TEDY NEPUJDE

    # translate_op_to_qiskit ??
    terms_translated = {}
    for k,v in fermion_operator.terms.items():
        terms_translated[ (" ").join([f"{'+' if i[1] else '-'}_{i[0]}" for i in k]) ] = v

    # print(f"started BK tangelo->qiskit fermiotic: {get_timestamp()}")

    qiskit_fermop = FermionicOp(terms_translated, num_spin_orbitals=fermion_operator.n_spinorbitals)
    
    # tohle je pro sfbk:
    # qiskit_fermop = qiskit_fermop.normal_order().simplify()
    # pokud obsahuje _data prazdnej '' klic, tak ho vyndej ven, protoze sfbk ho nepodporuje. udelat fix v qiskit-nature repu
    # const_val = qiskit_fermop._data.pop('', 0.0)   

    # print(f"started BK qiskit mapping: {get_timestamp()}")

    mapper = BravyiKitaevMapper()
    # mapper = BravyiKitaevSuperFastMapper()
    qiskit_qubitop = mapper.map(qiskit_fermop)
    tangelo_qubitop = translate_op_from_qiskit(qiskit_qubitop)

    # print(f"Mapping and translation qiskit->tangelo finished: {get_timestamp()}")

    # fermion_operator.compress(1e-3)
    # fermion_operator.compress()
    # print(len(fermion_operator.__dict__["terms"]))
    # qubit_operator = openfermion_bravyi_kitaev(fermion_operator, n_qubits=n_qubits)

    return tangelo_qubitop