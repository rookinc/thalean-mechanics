# Thalean Mechanics Vocabulary

This document defines the canonical vocabulary of Thalean Mechanics.

The words in this document are normative.

Their meanings may be extended but should not be redefined.

---

## Thalion

The primitive computational object.

A thalion is a finite computational object possessing a canonical 60-address space organized as a 5 x 3 x 4 hierarchy.

A thalion is not a bit.

---

## Address

A canonical location within a thalion.

Addresses are immutable identifiers.

Canonical form:

5?-3?-4?

Example:

5c-3b-4d

---

## Canonical Address Space

The complete set of sixty canonical addresses of a thalion.

The address space is intrinsic to the thalion.

---

## Registration

The canonical state of a thalion.

Registration is objective.

Observation is registration.

---

## Canonical Registration

The objective resolved registration of a thalion.

Canonical registration exists independently of any representation.

---

## Informative Action

A lawful action capable of changing canonical registration.

Examples include:

- pressing a button
- writing memory
- sewing a bartack
- moving a chess piece
- committing source code

---

## Registration Interpreter

A deterministic process that converts canonical registration into a representation.

Interpreters do not change canonical registration.

---

## Representation Completeness

A mechanics property of a lawful family of registration interpreters.

The family is representation-complete when its joint action is
faithful to Canonical Registration.

Representation Completeness does not require any individual
representation to be faithful.

---

## Joint Faithfulness

A property of a family of registration interpreters.

For

    I_j : R_T -> X_j,

the family is jointly faithful when

    I_j(r) = I_j(r') for every j

implies

    r = r'.

Equivalently, the diagonal interpreter is injective.

---

## Compatibility Locus

The set of representation tuples that arise from one lawful common
Canonical Registration.

For the diagonal interpreter

    Delta_I(r) = (I_j(r))_j,

the compatibility locus is

    C_I = image(Delta_I).

Compatibility is common-source consistency, not equality among
different representations.

---

## Representation

A representation produced from canonical registration.

Examples include:

- binary value
- graph
- visualization
- text
- sound
- address report

Representations are not the thalion.

---

## Bit

A binary representation produced by a binary registration interpreter.

A bit is not the primitive computational object.

---

## Computational Record

A durable record preserving a canonical registration.

Examples include:

- signed JSON
- xkernel receipt
- git commit
- SQL row
- NFT

A computational record is not the thalion.

---

## Context

The environment in which a thalion is evaluated or registered.

The same thalion may participate in multiple contexts.

Contexts do not redefine the thalion.

---

## Ontological Ordering

Reality
↓

Thalion
↓

Canonical Registration
↓

Computational Record
↓

Representation

