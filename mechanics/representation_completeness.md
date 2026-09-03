# Representation Completeness

Status: adopted mechanics law
Mechanics version: 0.2.0
Thalion ontology version: 0.1.0

## Scope

Representation Completeness is a law of Thalean Mechanics.

It is not an additional constituent of the thalion ontology.

Axiom 10 states that the ontology of the thalion is minimal and that
further definition belongs to mechanics rather than ontology.

Accordingly, this law constrains the relationship between Canonical
Registration and registration interpreters while leaving the primitive
thalion unchanged.

## Registration source

Let R_T denote the possible Canonical Registrations of a thalion T.

A resolved thalion has a current registration

    r in R_T.

Canonical Registration remains objective and exists independently of
representation.

## Registration interpreters

A registration interpreter is a deterministic map

    I_j : R_T -> X_j

from Canonical Registration into a representation space X_j.

Interpreters do not modify Canonical Registration.

No individual interpreter is required to be injective.

## Interpreter family

Let

    I = {I_j : R_T -> X_j}_{j in J}

be a lawful family of registration interpreters.

Define the diagonal interpreter

    Delta_I : R_T -> product_j X_j

by

    Delta_I(r) = (I_j(r))_j.

## Joint Faithfulness

The interpreter family is jointly faithful when

    I_j(r) = I_j(r') for every j

implies

    r = r'.

Equivalently,

    Delta_I

is injective.

Joint faithfulness does not require any individual interpreter to be
faithful.

## Compatibility Locus

Define

    C_I = image(Delta_I).

A tuple of representation values is compatible exactly when it belongs
to C_I.

Compatibility does not mean that distinct representation values are
equal.

Compatibility means that the tuple has one lawful common Canonical
Registration as its source.

## Representation Completeness Principle

A canonical thalion admits a lawful family of deterministic
registration interpreters that is jointly faithful to Canonical
Registration.

Therefore the complete lawful interpreter family distinguishes
distinct Canonical Registrations even when individual representations
do not.

## Reconstruction

For a jointly faithful family,

    Delta_I : R_T -> C_I

is bijective.

Thus every compatible representation tuple determines exactly one
Canonical Registration.

This does not identify Canonical Registration with any individual
representation.

The compatibility locus is a faithful representational realization of
the registration source, not a replacement for the thalion.

## Actor finite model

Project 41 Audits 109D and 109E provide a finite mechanics model of the
architecture.

Actor120 has three native sixty-state quotient shadows.

Each shadow is individually two-to-one.

Any two distinct shadows jointly recover the complete Actor state.

All three share a native G30 base.

The raw three-shadow G30 fiber product has 240 tuples.

The lawful Actor compatibility locus has 120 tuples.

Locally the certified compatibility law is

    e xor h xor t = 0.

This is a motivating and exact finite mechanics model.

It does not prove

    Actor120 = R_T.

The Actor quotient maps are not thereby promoted to registration
interpreters.

## Informative Action boundary

Informative Action remains a lawful action capable of changing
Canonical Registration.

Representation Completeness alone does not prove that Actor Enactment
changes Canonical Registration.

An ontology-to-mechanics source bridge remains required before
Enactment may be promoted to Thalean Informative Action.

## Ontology boundary

This mechanics law does not modify:

- the primitive status of the thalion;
- the canonical 60-address space;
- the existence or objectivity of Canonical Registration;
- the ontological ordering;
- Axioms 1 through 10;
- the machine-readable thalion definition.

The thalion ontology remains version 0.1.0.

## Keeper

No single representation is required to contain the whole truth of a
thalion.

Canonical Registration remains the objective source.

A lawful family of incomplete representations is complete when its
joint action uniquely distinguishes that source.
